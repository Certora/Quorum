# Quorum

Quorum is an open-source Python utility designed to verify the integrity of smart contracts deployed on blockchains. It fetches contract code directly from the blockchain and compares it with the official version provided by developers or customers in their GitHub repositories. This process helps identify discrepancies between the on-chain and official code, ensuring the contract deployed on the blockchain matches the intended version. By automating code comparison and streamlining the review of governance proposals, Quorum enhances the security and trustworthiness of smart contracts, helping users quickly detect unauthorized changes or errors.

## Features
- **Fetch Smart Contract Source Codes:** Retrieve source code directly from various blockchains using contract addresses.
- **Compare Local and Remote Codes:** Generate unified diffs to highlight differences between local and remote source codes.
- **Verify Code Against Known Reviewed Repositories:** Generate diffs against specifically defined trusted auditor's repositories.
- **Global Variable Check:** Ensure all global variables in unmatched contracts are either constant or immutable.
- **Feed Price Check:** Verify the feed price of a contract is mentioned on ChainLink.
- **New Listing Check:** Check if proposal contains a new Listing.
- **Automated Repository Management:** Clone or update repositories based on customer configurations.
- **Quick Setup Command:** Streamline initial configuration with a single setup command that generates necessary files and guides proper setup.

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

## Quick Setup

To simplify the initial configuration, Quorum provides a setup command that generates essential configuration files and guides you through the setup process.

### Using the Setup Command

Run the following command in your desired working directory (defaults to the current directory if not specified):

```sh
SetupQuorum [working_directory]
```

- **`working_directory`**: *(Optional)* Path to the desired working directory. Defaults to the current directory if not provided.

**Example:**

```sh
SetupQuorum ./my_quorum_project
```

This command will:
- Copy the following template files to your working directory:
  - `ground_truth.json`
  - `execution.json`
  - `.env.example`
  - `README.md`
- Provide guidance through comments within the configuration files and detailed Readme file to help you properly configure Quorum.

### Post-Setup Configuration

After running the setup command, perform the following steps:

1. **Configure Environment Variables:**

   Edit the `.env` file to include your actual API keys and desired paths:

   ```sh
   export ETHSCAN_API_KEY="your_etherscan_api_key"
   export ANTHROPIC_API_KEY="your_anthropic_api_key"
   export QUORUM_PATH="/path/to/your/quorum_directory"
   ```

2. **Fill Out Configuration Files:**

   - **`ground_truth.json`**: Define repositories and providers for each protocol.
   - **`execution.json`**: Specify proposal addresses for each network.
   - **`Readme.md`**: Follow the included guide to understand installation, configuration, available flags, and the checks performed by Quorum.

## Clarifications

As part of the tool's process, Quorum uses `solcx` to parse contract code to AST. The version of `solcx` used is the latest. If the contract code is not compatible with the latest version of `solcx`, the tool will not be able to parse the contract code and will not be able to proceed with the global variable and new listing checks.

## Environment Variables

Quorum requires specific environment variables to function correctly. These variables can be set in your shell or defined in a `.env` file.

### Required Environment Variables

- **ETHSCAN_API_KEY:** API key for Etherscan.
- **ANTHROPIC_API_KEY:** API key for Anthropic (required for advanced new listing first deposit checks).
- **QUORUM_PATH:** Path to specify where the repositories and diffs will be saved.

### Setting Environment Variables

**Using Shell:**

```sh
export ETHSCAN_API_KEY="your_etherscan_api_key"
export ANTHROPIC_API_KEY="your_anthropic_api_key"
export QUORUM_PATH="/path/to/artifacts"
```

**Using `.env` File:**

After running the setup command, a `.env` file will be present. fill in the required values:

Then edit `.env`:

```sh
ETHSCAN_API_KEY=your_etherscan_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
QUORUM_PATH="/path/to/artifacts"
```

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

**Example config file `config.json`:**

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

**To run using the config file:**

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

### Template for `ground_truth.json`:

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

**Fields explanation:**
- `ProtocolName`: Your protocol or organization name
- `dev_repos`: List of GitHub repositories containing your protocol's source code
- `review_repo`: Repository containing pre-deployment code for review
- `price_feed_providers`: List of supported price feed providers (Chainlink, Chronicle)
- `token_validation_providers`: List of supported token validation providers (Coingecko)

### Current Supported Providers

**Price Feed Providers:**
- Chainlink
- Chronicle

**Token Validation Providers:**
- Coingecko

## Artifacts Structure

Quorum generates and organizes artifacts in a structured manner under the `QUORUM_PATH` directory. Here is a general overview of the structure:

### Directory Structure

```
QUORUM_PATH/
├── ground_truth.json
├── CustomerName/
│   ├── modules/
│   │   ├── repository1/
│   │   ├── repository2/
│   │   ├── ...
│   ├── checks/
│   │   ├── ChainName/
│   │   │   ├── ProposalAddress1/
│   │   │   │   ├── DiffCheck_datetime/
│   │   │   │   │   ├── file1.patch
│   │   │   │   │   ├── file2.patch
│   │   │   │   ├── FeedPriceCheck_datetime/
│   │   │   │   │   ├── file1.json
│   │   │   │   ├── GlobalVariableCheck_datetime/
│   │   │   │   │   ├── file1.json
│   │   │   │   │   ├── ...
│   │   │   │   ├── NewListingCheck_datetime/
│   │   │   │   │   ├── file1.json
│   │   │   │   ├── ...
│   │   │   ├── ProposalAddress2/
│   │   │   ├── ...
│   │   ├── ...
│   │   ├── ProposalAddressN/
│   │   │   ├── ...
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
