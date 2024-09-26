# ProposalTools

ProposalTools is an open-source Python utility designed to fetch and compare smart contract source codes. It helps users identify and analyze differences between local and remote versions of smart contract code, making it easier to review changes and ensure code integrity.

## Features
- **Fetch Smart Contract Source Codes:** Retrieve source code directly from various blockchains using contract addresses.
- **Compare Local and Remote Codes:** Generate unified diffs to highlight differences between local and remote source codes.
- **Global Variable Check:** Ensure all global variables in unmatched contracts are either constant or immutable.
- **Automated Repository Management:** Clone or update repositories based on user configurations.

## Prerequisites
- Python 3.11 or higher

## Installation

You can install ProposalTools directly from GitHub using pip:

```sh
pip install git+https://github.com/YourUsername/ProposalTools.git
```

Or clone the repository:

```sh
git clone https://github.com/YourUsername/ProposalTools.git
```

Replace `YourUsername` with your GitHub username or the organization name where the repository is hosted.

## Environment Variables

Before using ProposalTools, you need to configure the following environment variables for API keys corresponding to each blockchain. These keys are necessary to access the respective blockchain explorers:

- **ETHERSCAN_API_KEY:** API key for Etherscan (Ethereum).
- **ARBISCAN_API_KEY:** API key for Arbiscan (Arbitrum).
- **AVALANCHESCAN_API_KEY:** API key for Avalanche Explorer (Avalanche). Defaults to "FREE" if not set.
- **BASESCAN_API_KEY:** API key for BaseScan (Base).
- **BSCSCAN_API_KEY:** API key for BscScan (Binance Smart Chain).
- **GNOSISSCAN_API_KEY:** API key for GnosisScan (Gnosis Chain).
- **METERSCAN_API_KEY:** API key for MeterScan (Meter). Defaults to "FREE" if not set.
- **OPTIMISM_API_KEY:** API key for Optimism Explorer (Optimism).
- **POLYGONSCAN_API_KEY:** API key for PolygonScan (Polygon).
- **SCROLLSCAN_API_KEY:** API key for ScrollScan (Scroll).
- **ZKSYNC_API_KEY:** API key for zkSync Explorer (zkSync).

You can set these environment variables in your shell:

```sh
export ETHERSCAN_API_KEY="your_etherscan_api_key"
export ARBISCAN_API_KEY="your_arbiscan_api_key"
export AVALANCHESCAN_API_KEY="your_avalanchescan_api_key"
export BASESCAN_API_KEY="your_basescan_api_key"
export BSCSCAN_API_KEY="your_bscscan_api_key"
export GNOSISSCAN_API_KEY="your_gnosisscan_api_key"
export METERSCAN_API_KEY="your_meterscan_api_key"
export OPTIMISM_API_KEY="your_optimism_api_key"
export POLYGONSCAN_API_KEY="your_polygonscan_api_key"
export SCROLLSCAN_API_KEY="your_scrollscan_api_key"
export ZKSYNC_API_KEY="your_zksync_api_key"
```

Replace `your_etherscan_api_key`, `your_arbiscan_api_key`, etc., with the actual API keys provided by the respective blockchain explorers.

Additionally, set the `PRP_TOOL_PATH` environment variable to specify where the repositories and diffs will be saved:

```sh
export PRP_TOOL_PATH="/path/to/artifacts"
```

Replace `/path/to/artifacts` with the path where you want the tool to save cloned repositories and diff files.

## Usage

To run the tool, use the command line:

```sh
CheckProposal --customer "ProjectName" --chain "ChainName" --proposal_address "Address"
```

OR

```sh
python3 ProposalTools/main.py --customer "ProjectName" --chain "ChainName" --proposal_address "Address"
```

Replace `ProjectName` with your project identifier, `ChainName` with the blockchain chain (e.g., "ETH", "AVAX"), and `Address` with the proposal address.

### Example Usage with Config File

You can also execute multiple tasks using a configuration file:

Example config file `config.json`:

```json
{
    "ProjectName": {
        "ETH": {
            "Proposals": ["0x1234567890abcdef1234567890abcdef12345678", "0xabcdef1234567890abcdef1234567890abcdef12"]
        },
        "AVAX": {
            "Proposals": ["0xabcdefabcdefabcdefabcdefabcdefabcdefabcdef"]
        },
        "BSC": {
            "Proposals": []
        }
    }
}
```

To run using the config file:

```sh
python3 ProposalTools/main.py --config path/to/config.json
```

**Note:** If the "Proposals" list for a particular chain is empty, the task for that chain will be skipped. This allows you to include or exclude chains from processing without modifying the code.

## Configuration

The `repos.json` file defines the repositories for each project. It should be located under the `PRP_TOOL_PATH`. If not found, a default `repos.json` configuration will be created.

Example `repos.json`:

```json
{
    "ProjectName": [
        "https://github.com/example/project-repo1",
        "https://github.com/example/project-repo2"
    ]
}
```

This configuration is used by the tool to manage the repositories.

## Artifacts Structure

ProposalTools generates and organizes artifacts in a structured manner under the `PRP_TOOL_PATH` directory. Here is a general overview of the structure:

### Directory Structure

```
PRP_TOOL_PATH/
├── ProjectName/
    ├── checks/
    │   ├── ProposalAddress1/
    │   │   ├── diffs_datetime/
    │   │   │   ├── file.patch
    │   │   ├── global_check_datetime/
    │   │   │   ├── file.json
    │   ├── ProposalAddress2/
    │   │   ├── ...
    ├── modules/
    │   ├── repository1/
    │   ├── repository2/
    │   ├── ...
    ├── execution.json
    ├── repos.json
```

### Description

- **ProjectName/**: This directory is named after your project, representing the context or organization for which the analysis is performed. Each project has its own directory.

  - **checks/**: Contains the diffs and global variable checks generated for each smart contract address analyzed. Each subdirectory is named after the contract's address and contains patch files highlighting differences between local and remote source codes, as well as JSON files documenting any global variables that are not constant or immutable.

  - **modules/**: This directory stores the cloned repositories for the project. Each subdirectory corresponds to a specific repository associated with the project, containing the source code and related files.

  - **execution.json**: This file stores the configuration and results of the last execution, including details like which proposals were checked and any findings or issues encountered.

  - **repos.json**: A configuration file specifying the repositories to be managed for the project. This file can be customized to include the URLs of the repositories related to the project.

### Example

For instance, the structure under the `PRP_TOOL_PATH/ProjectName/` directory might look like:

```
ProjectName/
├── checks/
│   ├── 0x1234567890abcdef1234567890abcdef12345678/
│   │   ├── diffs_20240801_105150/
│   │   │   ├── ContractName.patch
│   │   ├── global_check_20240801_105150/
│   │   │   ├── ContractName.json
│   ├── 0xabcdef1234567890abcdef1234567890abcdef12/
│   │   ├── ...
├── modules/
│   ├── project-repo1/
│   ├── project-repo2/
├── execution.json
├── repos.json
```

In this example, each proposal address under the `checks/` directory contains diff files that highlight the differences between the local and fetched source codes, as well as global variable check results. The `modules/` directory contains the repositories relevant to the project "ProjectName," and the `execution.json` and `repos.json` files hold metadata and configuration details.

## License

ProposalTools is released under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## Acknowledgments

- Thanks to all contributors and the open-source community.
