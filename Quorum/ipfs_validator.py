# ipfs_validator.py

from pathlib import Path
import argparse
import re
import requests

from Quorum.utils.chain_enum import Chain
import Quorum.utils.arg_validations as arg_valid
from Quorum.apis.block_explorers.chains_api import ChainAPI

from llm.chains.ipfs_validation_chain import IPFSValidationChain


IPFS_CACHE = Path(__file__).parent / '.ipfs_cache'
IPFS_CACHE.mkdir(exist_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Compare ipfs with actual payload.')
    parser.add_argument('--proposal_id', type=int, help='The id of the proposal.')
    parser.add_argument('--chain', type=str, choices=[chain.value for chain in Chain], help='Blockchain chain.')
    parser.add_argument('--proposal_address', type=arg_valid.validate_address, help='Ethereum proposal address.')
    parser.add_argument('--prompt_templates', type=list[str], nargs="+",
                        default=['ipfs_validation_prompt_part1.j2', "ipfs_validation_prompt_part2.j2"],
                        help='Jinja templates for prompting the LLM.')
    
    args = parser.parse_args()

    return args


# TODO: This function should be temporary, it is scraping the Aave Gov UI page's HTML 
#       of the proposal to get the ipfs link and it's pretty fragile.
#       We should remove this function once we implement a better way to get the data using an API that 
#       Aave is currently working on or their "v3-governance-cache" repo. This should be done on a different PR.
def get_raw_ipfs(proposal_id: int) -> str:
    cache = IPFS_CACHE / f'{proposal_id}.txt'
    if cache.exists():
        with open(cache) as f:
            return f.read()
    
    resp = requests.get(f'https://vote.onaave.com/proposal/?proposalId={proposal_id}')
    resp.raise_for_status()
    voting_ui_html = resp.content.decode()

    # Somewhere in the HTML there's a js script that contains a json with the following field:
    # "ipfsHash": "<ipfs_hash>". We want to get the ipfs_hash to construct the link to the raw ipfs.
    # The json also has \\" to mark these are special characters.
    # ipfs_hash = voting_ui_html.replace('\\', '').split('"ipfsHash":')[1].split(',')[0].replace('"', '')
    match = re.search(r'\\"ipfsHash\\":\s*\\"(.*?)\\"', voting_ui_html)
    if not match:
        raise ValueError('ipfsHash not found in the HTML.')
    
    ipfs_hash = match.group(1)
    
    resp = requests.get(f'https://ipfs.io/ipfs/{ipfs_hash}')
    resp.raise_for_status()
    
    content = resp.content.decode()
    with open(cache, 'w') as f:
        f.write(content)
    return content


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
