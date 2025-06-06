import argparse
from pathlib import Path

import requests

import quorum.utils.pretty_printer as pp
from quorum.apis.block_explorers.chains_api import ChainAPI
from quorum.llm.chains.ipfs_validation_chain import IPFSValidationChain
from quorum.utils.quorum_configuration import QuorumConfiguration

IPFS_CACHE = Path(__file__).parent / ".ipfs_cache"
IPFS_CACHE.mkdir(exist_ok=True)


def get_raw_ipfs(proposal_id: int) -> str:
    cache = IPFS_CACHE / f"{proposal_id}.txt"
    if cache.exists():
        with open(cache) as f:
            return f.read()

    resp = requests.get(
        "https://raw.githubusercontent.com/bgd-labs/v3-governance-cache/refs/heads/main/cache/"
        f"1/0x9AEE0B04504CeF83A65AC3f0e838D0593BCb2BC7/proposals/{proposal_id}.json"
    )
    resp.raise_for_status()

    proposal_data = resp.json()
    ipfs_content = proposal_data["ipfs"]["description"]

    with open(cache, "w") as f:
        f.write(ipfs_content)

    return ipfs_content


def run_ipfs_validator(args: argparse.Namespace):
    """
    Validates IPFS content against proposal source code using LLM-based analysis.
    This function performs validation between IPFS content and smart contract source code
    by leveraging Language Model analysis through a validation chain.
    Args:
        args (argparse.Namespace): Command line arguments containing:
            - chain: The blockchain network to query
            - proposal_address: Contract address of the proposal
            - proposal_id: IPFS identifier for the proposal
            - prompt_templates: Templates for LLM prompts
    Raises:
        ValueError: If ANTHROPIC_API_KEY is not set in environment variables
        ValueError: If no source code is found for the given proposal address
    Returns:
        None. Results are printed to stdout:
            - Lists incompatibilities if found
            - Warning message if no incompatibilities detected
    Example:
        args = parser.parse_args()
        run_ipfs_validator(args)
    """
    # Check if the Anthropic API key is set in environment variables
    if not QuorumConfiguration().anthropic_api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable is not set. Please set it to use this functionality."
        )

    # Initialize Chain API and fetch source codes
    block_explorer = ChainAPI(args.chain)
    source_codes = block_explorer.get_source_code(args.payload_address)
    if not source_codes:
        raise ValueError("No source codes found for the given proposal address.")
    # Extract the CONTRACT_NAME code source from the source codes
    contract_name = args.contract_name
    source_code = next(
        (code for code in source_codes if contract_name in code.file_name),
        None,
    )
    if not source_code:
        raise ValueError(f"No source code found for the contract name: {contract_name}")

    payload = "\n".join(source_code.file_content)

    # Fetch IPFS content
    ipfs = get_raw_ipfs(args.proposal_id)

    # Initialize the IPFS Validation Chain
    ipfs_validation_chain = IPFSValidationChain()

    try:
        # Execute the Chain
        answer = ipfs_validation_chain.execute(
            prompt_templates=args.prompt_templates, ipfs=ipfs, payload=payload
        )
    except Exception as e:
        pp.pprint(f"Got and error while running LLM: {e}", pp.Colors.FAILURE)
        pp.pprint("Verify your API key and try again.", pp.Colors.FAILURE)
        return

    if answer.incompatibilities:
        pp.pprint("Found incompatibilities:", pp.Colors.FAILURE)
        for incompatibility in answer.incompatibilities:
            pp.pprint(pp.SEPARATOR_LINE, pp.Colors.INFO)
            pp.pprint("Subject:", pp.Colors.SUCCESS)
            pp.pprint(incompatibility.subject, pp.Colors.INFO)
            pp.pprint("Details in IPFS:", pp.Colors.WARNING)
            pp.pprint(incompatibility.subject_in_ipfs, pp.Colors.INFO)
            pp.pprint("Details in Solidity:", pp.Colors.WARNING)
            pp.pprint(incompatibility.subject_in_solidity, pp.Colors.INFO)
            pp.pprint("Description:", pp.Colors.WARNING)
            pp.pprint(incompatibility.description, pp.Colors.INFO)
            pp.pprint(pp.SEPARATOR_LINE, pp.Colors.INFO)
    else:
        pp.pprint(
            "LLM found no incompatibilities. Please Check manually.", pp.Colors.WARNING
        )
