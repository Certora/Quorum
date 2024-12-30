# Quorum

Quorum is an open-source Python utility designed to verify the integrity of smart contracts deployed on blockchains. It fetches contract code directly from the blockchain and compares it with the official version provided by developers or customers in their GitHub repositories. This process helps identify discrepancies between the on-chain and official code, ensuring the contract deployed on the blockchain matches the intended version. By automating code comparison and streamlining the review of governance proposals, Quorum enhances the security and trustworthiness of smart contracts, helping users quickly detect unauthorized changes or errors.

## Features
- **Fetch Smart Contract Source Codes:** Retrieve source code directly from various blockchains using contract addresses.
- **Compare Local and Remote Codes:** Generate unified diffs to highlight differences between local and remote source codes.
- **Verify Code Against Known Reviewed Repositories:** Generate diffs against specifically defined trusted auditor's repositories.
- **Global Variable Check:** Ensure all global variables in unmatched contracts are either constant or immutable.
- **Feed Price Check:** Verify the feed price of a contract is mentioned on ChainLink.
- **New Listing Check:** Check if proposal contain a new Listing.
- **Automated Repository Management:** Clone or update repositories based on customer configurations.

## Prerequisites
- Python 3.11 or higher

## Installation

You can install Quorum directly from GitHub using pip:

```sh
pip install git+ssh://git@github.com/Certora/Quorum.git
```

Or clone the repository:

```sh
git clone git@github.com:Certora/Quorum.git
```

## Clarifications

As part of tool process, the tool will use solcx to parse the contract code to AST. the version of solcx used is the latest. If the contract code is not compatible with the latest version of solcx, the tool will not be able to parse the contract code and will not be able to proceed with the global variable and new listing checks.

## Environment Variables

Before using Quorum, you need to configure the following environment variable for the Etherscan API key. This key is necessary to access the respective blockchain explorers:

- **ETHSCAN_API_KEY:** API key for Etherscan.

And for the new advanced new listing first deposit check, you need to configure the ANTHROPIC_API_KEY This key is necessary to access the Antropic API.

You can set these environment variables in your shell:

```sh
export ETHSCAN_API_KEY="your_etherscan_api_key"
export ANTHROPIC_API_KEY="your_anthropic_api_key"
```

Replace `your_etherscan_api_key`, `your_anthropic_api_key` with your actual API keys.

Alternatively, you can set these environment variables in a `.env` file in the current working directory where you use the tool:

```sh
ETHSCAN_API_KEY=your_etherscan_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```


Additionally, set the `QUORUM_PATH` environment variable to specify where the repositories and diffs will be saved:

```sh
export QUORUM_PATH="/path/to/artifacts"
```

Replace `/path/to/artifacts` with the path where you want the tool to save cloned repositories and diff files.

## Usage

To run the tool, use the command line:

```sh
CheckProposal --customer "CustomerName" --chain "ChainName" --proposal_address "Address"
```

OR

```sh
python3 Quorum/check_proposal.py --customer "CustomerName" --chain "ChainName" --proposal_address "Address"
```

Replace `CustomerName` with the customer identifier, `ChainName` with the blockchain chain, and `Address` with the proposal address.

### Example Usage with Config File

You can also execute multiple tasks using a configuration file:

Example config file `config.json`:

```json
{
    "Aave": {
        "Ethereum": {
            "Proposals": [
                "0xAD6c03BF78A3Ee799b86De5aCE32Bb116eD24637"
            ]
        },
        "Arbitrum": {
            "Proposals": [
                "0x22ca2Dd3063189F9E7e76fA3078E2d916B3998b7"
            ]
        },
        "Avalanche": {
            "Proposals": []
        },
        "Base": {
            "Proposals": [
                "0x6B96B41a531713a141F6EcBbae80715601d0e456"
            ]
        },
        "BNBChain": {
            "Proposals": [
                "0xb4F2786984093eaE1D6Be2B4F8c8e3c2cb018b54"
            ]
        },
        "Gnosis": {
            "Proposals": []
        },
        "Metis": {
            "Proposals": []
        },
        "Optimism": {
            "Proposals": []
        },
        "Polygon": {
            "Proposals": [
                "0x2dbBe7E30CD959A192FeFCEd9A5ae681d540deB4"
            ]
        },
        "Scroll": {
            "Proposals": [
                "0x9d9892256dF8f97d0c15F4494aa5D44D376CC749"
            ]
        },
        "zkSync": {
            "Proposals": []
        }
    }
}
```

To run using the config file:

```sh
python3 Quorum/check_proposal.py --config path/to/config.json
```

Or if you used the pip installation:

```sh
CheckProposal --config path/to/config.json
```

**Note:** If the "Proposals" list for a particular chain is empty, the task for that chain will be skipped. This allows you to include or exclude chains from processing without modifying the code.

## Configuration

The `ground_truth.json` file defines the repositories for each customer. It should be located under the `QUORUM_PATH`. If not found, a default `ground_truth.json` configuration will be created.


Template for `ground_truth.json`:

```json
{
    "ProtocolName": {
        "dev_repos": [
            "https://github.com/organization/repository1",
            "https://github.com/organization/repository2"
        ],
        "review_repo": "https://github.com/organization/review-repository",
        "price_feed_providers": ["Chainlink", "Chronicle"],
        "token_validation_providers": ["Coingecko"]
    }
}
```

Fields explanation:
- `ProtocolName`: Your protocol or organization name
- `dev_repos`: List of GitHub repositories containing your protocol's source code
- `review_repo`: Repository containing pre-deployment code for review
- `price_feed_providers`: List of supported price feed providers (Chainlink, Chronicle)
- `token_validation_providers`: List of supported token validation providers (Coingecko)
```

Example `ground_truth.json`:

```json
{
    "Aave": 
    {
        "dev_repos":
        [
            "https://github.com/bgd-labs/aave-helpers",
            "https://github.com/bgd-labs/aave-address-book",
            "https://github.com/aave-dao/aave-v3-origin"
        ],
        "review_repo": "https://github.com/bgd-labs/aave-proposals-v3",
        "price_feed_providers": ["Chainlink"],
        "token_validation_providers": ["Coingecko"]
    }
}
```

This configuration is used by the tool to manage the ground truth information for each customer. The `dev_repos` array contains the URLs of the repositories associated with the customer. The `review_repo` field specifies the repository to compare against when checking proposals. The `price_feed_providers` array lists the feed price providers to check against (e.g., "Chainlink", "Chronicle"). The `token_validation_providers` array lists the token validation providers to check against (e.g., "Coingecko").

### current supported price feed providers are
- Chainlink
- Chronicle

## Current supported token validation providers are
- Coingecko

## Artifacts Structure

Quorum generates and organizes artifacts in a structured manner under the `QUORUM_PATH` directory. Here is a general overview of the structure:

### Directory Structure

```
QUORUM_PATH/
├── ground_truth.json
├── CustomerName/
|     ├── modules/
|     │   ├── repository1/
|     │   ├── repository2/
|     │   ├── ...
|     ├── checks/
|     |   ├── ChainName/
|     |   │   ├── ProposalAddress1/
|     |   │   │   ├── DiffCheck_datetime/
|     |   │   │   │   ├── file1.patch
|     |   │   │   │   ├── file2.patch
|     |   │   │   ├── FeedPriceCheck_datetime/
|     |   │   │   │   ├── file1.json
|     |   │   │   ├── GlobalVariableCheck_datetime/
|     |   │   │   │   ├── file1.json
|     |   │   │   │   ├── ...
|     |   │   │   ├── NewListingCheck_datetime/
|     |   │   │   │   ├── file1.json
|     |   │   │   ├── ...
|     |   │   ├── ProposalAddress2/
|     |   |   ├── ...
|     |   ├── ...
|     |   ├── ProposalAddressN/
|     |   |   ├── ...
```

### Description

- **CustomerName/**: This directory is named after the customer, representing the context or organization for which the analysis is performed. Each customer has its own directory.

  - **checks/**: Contains the diffs and global variable checks generated for each smart contract address analyzed. Each subdirectory is named after the contract's address and contains patch files highlighting differences between local and remote source codes, as well as JSON files documenting any global variables that are not constant or immutable.

  - **modules/**: This directory stores the cloned repositories for the customer. Each subdirectory corresponds to a specific repository associated with the customer, containing the source code and related files.

  - **execution.json**: This file stores the configuration and results of the last execution, including details like which proposals were checked and any findings or issues encountered.

  - **ground_truth.json**: A configuration file specifying the repositories to be managed for the customer. This file can be customized to include the URLs of the repositories related to the customer.

### Example

For instance, the structure under the `QUORUM_PATH/Aave/` directory might look like:

```
Aave/
├── checks/
│   ├── 0x065DF1F9d0aeDEa11E6d059ce29e91d2Abed59fA/
│   │   ├── diffs_20240801_105150/
│   │   │   ├── AaveV3Ethereum.patch
│   │   ├── global_check_20240801_105150/
│   │   │   ├── AaveV3Ethereum.json
│   ├── 0x564Dfd09eBB63F7e468401AffE2d8c2cDD08D68D/
│   │   ├── ...
│   ├── 0x683FdF51d5898F92317F870B25a6A4dF67dC58Ab/
│   │   ├── ...
│   ├── 0xF0221Fc5a2F825bbF6F994f30743aD5AAC66cd4E/
│   │   ├── ...
├── modules/
│   ├── aave-address-book/
│   ├── aave-helpers/
│   ├── aave-v3-origin/
├── execution.json
├── ground_truth.json
```

In this example, each proposal address under the `checks/` directory contains diff files that highlight the differences between the local and fetched source codes, as well as global variable check results. The `modules/` directory contains the repositories relevant to the customer "Aave," and the `execution.json` and `ground_truth.json` files hold metadata and configuration details.

## License

Quorum is released under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## Acknowledgments

- Thanks to all contributors and the open-source community.
