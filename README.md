## ProposalTools

ProposalTools is a Python-based utility designed to fetch and compare smart contract source codes. It helps users to identify and analyze differences between local and remote versions of smart contract code.

### Features
- **Fetch Smart Contract Source Codes:** Retrieve source code directly from Etherscan using a contract address.
- **Compare Local and Remote Codes:** Generate unified diffs to highlight differences between local and remote source codes.
- **Automated Repository Management:** Clone or update repositories based on customer configurations.

### Prerequisites
- Python 3.6 or higher

### Installation

You can install ProposalTools directly from GitHub using pip:

```sh
pip install git+ssh://git@github.com/Certora/ProposalTools.git
```

Or clone:

```sh
git clone git@github.com:Certora/ProposalTools.git
```

### Environment Variables

Before using ProposalsTool, you need to configure the following environment variables:

- **ETHSCAN_API_KEY:** This is the API key used to access the Etherscan API. You can obtain an API key by registering on the Etherscan website.

  Set the environment variable in your shell:

  ```sh
  export ETHSCAN_API_KEY="your_etherscan_api_key"
  ```

  Replace `your_etherscan_api_key` with the actual API key provided by Etherscan.

- **ProposalsToolArtifactsPath:** This is the path where the repositories and diffs will be saved. Ensure this directory exists and is writable.

  Set the environment variable in your shell:

  ```sh
  export ProposalsToolArtifactsPath="/path/to/artifacts"
  ```

  Replace `/path/to/artifacts` with the path where you want the tool to save cloned repositories and diff files.

### Usage

To run the tool, use the command line:

```sh
CheckProposal --customer "CustomerName" --proposal_address "EthereumContractAddress"
```

OR

```sh
python3 ProposalTools/main.py   --customer CustomerName --proposal_address EthereumContractAddress
```



Replace `CustomerName` with the customer identifier and `EthereumContractAddress` with the smart contract's Ethereum address.

### Configuration

The `repos.json` file defines the repositories for each customer. The structure is as follows:

```json
{
    "CustomerName": [
        "https://github.com/path/to/repo1",
        "https://github.com/path/to/repo2"
    ]
}
```

This configuration is used by the tool to manage the repositories.