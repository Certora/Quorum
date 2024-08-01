# ProposalTools

ProposalTools is a Python-based utility designed to fetch and compare smart contract source codes. It helps users identify and analyze differences between local and remote versions of smart contract code.

## Features
- **Fetch Smart Contract Source Codes:** Retrieve source code directly from various blockchains using contract addresses.
- **Compare Local and Remote Codes:** Generate unified diffs to highlight differences between local and remote source codes.
- **Automated Repository Management:** Clone or update repositories based on customer configurations.

## Prerequisites
- Python 3.11 or higher

## Installation

You can install ProposalTools directly from GitHub using pip:

```sh
pip install git+ssh://git@github.com/Certora/ProposalTools.git
```

Or clone the repository:

```sh
git clone git@github.com:Certora/ProposalTools.git
```

## Environment Variables

Before using ProposalTools, you need to configure the following environment variables for API keys corresponding to each blockchain. These keys are necessary to access the respective blockchain explorers:

- **ETHSCAN_API_KEY:** API key for Etherscan (Ethereum).
- **ARBSCAN_API_KEY:** API key for Arbiscan (Arbitrum).
- **AVAXSCAN_API_KEY:** API key for AvaScan (Avalanche). Defaults to "FREE" if not set.
- **BASESCAN_API_KEY:** API key for BaseScan (Base).
- **BSCSCAN_API_KEY:** API key for BscScan (Binance Smart Chain).
- **GNOSCAN_API_KEY:** API key for GnoScan (Gnosis Chain).
- **METSCAN_API_KEY:** API key for MetScan (Meter). Defaults to "FREE" if not set.
- **OPTSCAN_API_KEY:** API key for OptScan (Optimism).
- **POLYSCAN_API_KEY:** API key for PolygonScan (Polygon).
- **SCRSCAN_API_KEY:** API key for ScrollScan (Scroll).

You can set these environment variables in your shell:

```sh
export ETHSCAN_API_KEY="your_etherscan_api_key"
export ARBSCAN_API_KEY="your_arbiscan_api_key"
export AVAXSCAN_API_KEY="your_avaxscan_api_key"
export BASESCAN_API_KEY="your_basescan_api_key"
export BSCSCAN_API_KEY="your_bscscan_api_key"
export GNOSCAN_API_KEY="your_gnoscan_api_key"
export METSCAN_API_KEY="your_metscan_api_key"
export OPTSCAN_API_KEY="your_optscan_api_key"
export POLYSCAN_API_KEY="your_polyscan_api_key"
export SCRSCAN_API_KEY="your_scrscan_api_key"
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
CheckProposal --customer "CustomerName" --chain "ChainName" --proposal_address "Address"
```

OR

```sh
python3 ProposalTools/main.py --customer "CustomerName" --chain "ChainName" --proposal_address "Address"
```

Replace `CustomerName` with the customer identifier, `ChainName` with the blockchain chain (e.g., "ETH", "AVAX"), and `Address` with the proposal address.

### Example Usage with Config File

You can also execute multiple tasks using a configuration file:

Example config file `config.json`:

```json
{
    "Aave": {
        "AVAX": {
            "Proposals": ["0x564Dfd09eBB63F7e468401AffE2d8c2cDD08D68D"]
        },
        "ETH": {
            "Proposals": ["0x683FdF51d5898F92317F870B25a6A4dF67dC58Ab", "0x065DF1F9d0aeDEa11E6d059ce29e91d2Abed59fA"]
        },
        "GNO": {
            "Proposals": ["0xF0221Fc5a2F825bbF6F994f30743aD5AAC66cd4E"]
        },
        "ARB": {
            "Proposals": []
        },
        "BASE": {
            "Proposals": []
        },
        "BSC": {
            "Proposals": []
        },
        "MET": {
            "Proposals": []
        },
        "OPT": {
            "Proposals": []
        },
        "POLY": {
            "Proposals": []
        },
        "SCR": {
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

The `repos.json` file defines the repositories for each customer. It should be located under the `PRP_TOOL_PATH`. If not found, the following default `repos.json` configuration will be created:

```json
{
    "Aave": [
        "https://github.com/bgd-labs/aave-helpers",
        "https://github.com/bgd-labs/aave-address-book",
        "https://github.com/aave-dao/aave-v3-origin"
    ]
}
```

This configuration is used by the tool to manage the repositories.