import argparse
import requests
from pathlib import Path

from Quorum.apis.block_explorers.chains_api import ChainAPI
from Quorum.llm.chains.ipfs_validation_chain import IPFSValidationChain
from Quorum.utils.quorum_configuration import QuorumConfiguration
import Quorum.utils.pretty_printer as pp


IPFS_CACHE = Path(__file__).parent / '.ipfs_cache'
IPFS_CACHE.mkdir(exist_ok=True)


def get_raw_ipfs(proposal_id: int) -> str:
    cache = IPFS_CACHE / f'{proposal_id}.txt'
    if cache.exists():
        with open(cache) as f:
            return f.read()
    
    resp = requests.get('https://raw.githubusercontent.com/bgd-labs/v3-governance-cache/refs/heads/main/cache/'
                        f'1/0x9AEE0B04504CeF83A65AC3f0e838D0593BCb2BC7/proposals/{proposal_id}.json')
    resp.raise_for_status()

    proposal_data = resp.json()
    ipfs_content = proposal_data['ipfs']['description']

    with open(cache, 'w') as f:
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
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set. Please set it to use this functionality.")

    # Initialize Chain API and fetch source codes
    block_explorer = ChainAPI(args.chain)
    source_codes = block_explorer.get_source_code(args.payload_address)
    if not source_codes:
        raise ValueError("No source codes found for the given proposal address.")
    payload = '\n'.join(source_codes[0].file_content)

    # Fetch IPFS content
    ipfs = get_raw_ipfs(args.proposal_id)

    # Initialize the IPFS Validation Chain
    ipfs_validation_chain = IPFSValidationChain()

    # Execute the Chain
    answer = ipfs_validation_chain.execute(
        prompt_templates = args.prompt_templates, ipfs=ipfs, payload=payload
    )
    
    if answer.incompatibilities:
        pp.pprint("Found incompatibilities:", pp.Colors.FAILURE)
        for incompatibility in answer.incompatibilities:
            pp.pprint(incompatibility, pp.Colors.FAILURE)
    else:
        pp.pprint("LLM found no incompatibilities. Please Check manually.", pp.Colors.WARNING)
