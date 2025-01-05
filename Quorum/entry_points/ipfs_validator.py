import argparse
from pathlib import Path

import requests

import Quorum.utils.arg_validations as arg_valid
import Quorum.utils.config as config
import Quorum.utils.pretty_printer as pp
from Quorum.apis.block_explorers.chains_api import ChainAPI
from Quorum.llm.chains.ipfs_validation_chain import IPFSValidationChain
from Quorum.utils.chain_enum import Chain

IPFS_CACHE = Path(__file__).parent / ".ipfs_cache"
IPFS_CACHE.mkdir(exist_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare ipfs with actual payload.")
    parser.add_argument("--proposal_id", type=int, help="The id of the proposal.")
    parser.add_argument(
        "--chain",
        type=str,
        choices=[chain.value for chain in Chain],
        help="Blockchain chain.",
    )
    parser.add_argument(
        "--proposal_address",
        type=arg_valid.validate_address,
        help="Ethereum proposal address.",
    )
    parser.add_argument(
        "--prompt_templates",
        type=str,
        nargs="+",
        default=["ipfs_validation_prompt_part1.j2", "ipfs_validation_prompt_part2.j2"],
        help="Jinja templates for prompting the LLM.",
    )

    args = parser.parse_args()

    return args


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


def main():
    # Check if the Anthropic API key is set in environment variables
    if not config.ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set. Please set it to use this functionality.")
    args = parse_args()

    # Initialize Chain API and fetch source codes
    block_explorer = ChainAPI(args.chain)
    source_codes = block_explorer.get_source_code(args.proposal_address)
    if not source_codes:
        raise ValueError("No source codes found for the given proposal address.")
    payload = "\n".join(source_codes[0].file_content)

    # Fetch IPFS content
    ipfs = get_raw_ipfs(args.proposal_id)

    # Initialize the IPFS Validation Chain
    ipfs_validation_chain = IPFSValidationChain()

    # Execute the Chain
    answer = ipfs_validation_chain.execute(prompt_templates=args.prompt_templates, ipfs=ipfs, payload=payload)

    if answer.incompatibilities:
        pp.pretty_print("Found incompatibilities:", pp.Colors.FAILURE)
        for incompatibility in answer.incompatibilities:
            pp.pretty_print(incompatibility, pp.Colors.FAILURE)
    else:
        pp.pretty_print("LLM found no incompatibilities. Please Check manually.", pp.Colors.WARNING)


if __name__ == "__main__":
    main()
