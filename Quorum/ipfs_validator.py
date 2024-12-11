from Quorum.utils.chain_enum import Chain
import Quorum.utils.arg_validations as arg_valid
from Quorum.apis.block_explorers.chains_api import ChainAPI
from Quorum.llm.chains.ipfs_validation_chain import IPFSValidationChain

from pathlib import Path
import argparse
import requests


IPFS_CACHE = Path(__file__).parent / '.ipfs_cache'
IPFS_CACHE.mkdir(exist_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Compare ipfs with actual payload.')
    parser.add_argument('--proposal_id', type=int, help='The id of the proposal.')
    parser.add_argument('--chain', type=str, choices=[chain.value for chain in Chain], help='Blockchain chain.')
    parser.add_argument('--proposal_address', type=arg_valid.validate_address, help='Ethereum proposal address.')
    parser.add_argument('--prompt_templates', type=str, nargs="+",
                        default=['ipfs_validation_prompt_part1.j2', "ipfs_validation_prompt_part2.j2"],
                        help='Jinja templates for prompting the LLM.')
    
    args = parser.parse_args()

    return args

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


def main():
    args = parse_args()

    # Initialize Chain API and fetch source codes
    block_explorer = ChainAPI(args.chain)
    source_codes = block_explorer.get_source_code(args.proposal_address)
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

    # Output the LLM's response
    print(answer)
    

if __name__ == '__main__':
    main()
