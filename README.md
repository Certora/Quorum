# Quorum

Quorum is an open-source Python utility that ensures the integrity of smart contracts deployed on blockchains. By comparing on-chain code against known official repositories, Quorum helps detect unauthorized changes, bolstering the security and trustworthiness of decentralized systems.

## Key Features
1. **Fetch & Compare Smart Contract Source Codes:**  
   - Retrieves source code directly from various block explorers via contract addresses.  
   - Generates unified diffs highlighting differences between local and fetched source codes.  

2. **Repository & Code Verification:**  
   - Compare code against audited or reviewed repositories to confirm authenticity.  
   - Automates repository management (clone & update) based on your configuration.  

3. **Global Variable Check:**  
   - Ensures all unmatched contracts’ global variables are constant or immutable.  

4. **Feed Price Check:**  
   - Validates that the contract feed price is listed on recognized providers like Chainlink or Chronicle.  

5. **New Listing Check:**  
   - Checks if a given proposal introduces a new asset listing on the protocol.  

6. **Quick Setup Command:**  
   - Generates essential configuration files (`.env.example`, `ground_truth.json`, `execution.json`, etc.)  
   - Guides you through environment variable and repository configuration steps.  

---

## Prerequisites

- **Python 3.11 or higher**  
  Quorum requires Python 3.11+, as it utilizes features from the most recent Python release.

---

## Installation

### Via `pip`

#### Using pypi:
```bash
pip install certora-quorum
```

#### Using git+https:
```bash
pip install git+ssh://git@github.com/Certora/Quorum.git
```

### Or clone the repository:

```bash
git clone git@github.com:Certora/Quorum.git
```

---

## Quick Setup

Quorum offers a convenient setup command to streamline initial configuration by creating required files and providing guidance.

### 1. Run Setup Command

```bash
Quorum setup --working_dir "/home/user/quorum_project"
```

- **`working_directory`** *(Optional)*: Path where Quorum’s configuration files will be placed. If omitted, the current directory is used.

**Example**:
```bash
Quorum setup --working_dir ./my_quorum_project
```

This action will:
- Create the specified (or default) directory if it doesn’t exist.
- Copy **four** template files:
  1. `ground_truth.json`
  2. `execution.json`
  3. `.env.example`
  4. `README.md`
- Provide inline comments within these files for guidance.

### 2. Post-Setup Configuration

1. **Environment Variables**  
   Edit the `.env` file (or your shell profile) with your actual API keys and custom paths:
   ```bash
   export ETHSCAN_API_KEY="your_etherscan_api_key"
   export ANTHROPIC_API_KEY="your_anthropic_api_key"
   export QUORUM_PATH="/path/to/your/quorum_directory"
   ```

2. **Configuration Files**  
   - **`ground_truth.json`**: Define repositories and providers (e.g., price feed providers, token validation).  
   - **`execution.json`**: Specify proposal addresses to be checked for different chains.  
   - **`README.md`**: An auto-generated resource explaining your next steps.

3. **Optional: Command Autocompletion**
   Enable Quorum command autocompletion by adding this line to your shell profile (`.bashrc` or `.zshrc`):
   ```bash
      eval "$(register-python-argcomplete quorum)"
   ```
---

## Clarifications

Quorum leverages `solcx` (latest version) to parse contract code into an AST. Contracts incompatible with the latest `solc` version may break checks involving AST parsing (e.g., global variable checks, new listing checks).

---

## Environment Variables

To fully enable Quorum’s checks, set the following:

### Required Variables
- **`ETHSCAN_API_KEY`**: Your Etherscan API key (for block explorer queries).  
- **`ANTHROPIC_API_KEY`**: Required if you intend to use advanced LLM-based checks (e.g., new listing first deposit checks).  
- **`QUORUM_PATH`**: Directory path where Quorum stores cloned repos, diffs, logs, etc.

### Setting Variables

1. **Shell Environment:**

   ```bash
   export ETHSCAN_API_KEY="your_etherscan_api_key"
   export ANTHROPIC_API_KEY="your_anthropic_api_key"
   export QUORUM_PATH="/path/to/quorum_artifacts"
   ```

2. **`.env` File:**

   ```
   ETHSCAN_API_KEY=your_etherscan_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   QUORUM_PATH="/path/to/quorum_artifacts"
   ```

*(This file is automatically created by `Quorum setup` if not already present.)*

---

## Usage

Quorum now provides a **single CLI** with multiple **subcommands** for different tasks. Below is an overview of each subcommand, with examples.

### 1. **validate-address**

**Purpose:** Analyzes a single proposal address for a specific customer on a given chain.

```bash
Quorum validate-address --customer "Aave" --chain "Ethereum" --proposal_address "0xAD6..."
```

### 2. **validate-batch**

**Purpose:** Processes multiple proposals in bulk using a JSON config file.

```bash
Quorum validate-batch --config "/path/to/config.json"
```
*(See “**Example Usage with Config File**” for a sample config.)*

### 3. **validate-by-id**

**Purpose:** Looks up all payload addresses for a single proposal ID (useful for proposals containing multiple payloads).

```bash
Quorum validate-by-id --customer "Aave" --proposal_id 137
```

### 4. **validate-ipfs**

**Purpose:** Validates whether the IPFS description content aligns with the actual on-chain payload. Uses LLM-based analysis.

```bash
Quorum validate-ipfs --proposal_id 132 --chain "Ethereum" --proposal_address "0xAD6..."
```

### 5. **create-report**

**Purpose:** Generates a human-readable report of the proposal details, leveraging Jinja2 templates.

```bash
Quorum create-report --proposal_id 137 \
                     --template "Quorum/auto_report/AaveReportTemplate.md.j2" \
                     --generate_report_path "reports/v3-137.md"
```

### 6. **setup**

**Purpose:** Bootstraps your Quorum environment, creating `.env`, `ground_truth.json`, `execution.json`, and an initial `README.md`.

```bash
Quorum setup --working_dir "/home/user/quorum_project"
```

*(Refer to “**Quick Setup**” for details.)*

---

## Example Usage with Config File

For bulk execution, create a config file (e.g., `config.json`) with the following format:

```json
{
    "Aave": {
        "Ethereum": { "Proposals": [ "0xAD6..." ] },
        "Arbitrum": { "Proposals": [ "0x22ca2..." ] },
        ...
    }
}
```

Then run:

```bash
Quorum config --config config.json
```

*(Chains without proposals are automatically skipped.)*

---

## Configuration Details

### ground_truth.json

Defines each protocol’s repositories and providers:

```json
{
    "ProtocolName": {
        "dev_repos": [
            "https://github.com/org/repo1",
            "https://github.com/org/repo2"
        ],
        "review_repo": "https://github.com/org/review",
        "price_feed_providers": ["Chainlink", "Chronicle"],
        "token_validation_providers": ["Coingecko"]
    }
}
```

### Currently Supported Providers
- **Price Feeds**: Chainlink, Chronicle  
- **Token Validation**: Coingecko  

---

## Artifacts Structure

All artifacts (cloned repos, diffs, logs) are stored under `QUORUM_PATH`. Below is a typical folder hierarchy:

```
QUORUM_PATH/
├── ground_truth.json
├── CustomerName/
│   ├── modules/
│   │   ├── repository1/
│   │   ├── repository2/
│   ├── checks/
│   │   ├── ChainName/
│   │   │   ├── ProposalAddress/
│   │   │   │   ├── DiffCheck_<timestamp>/
│   │   │   │   ├── FeedPriceCheck_<timestamp>/
│   │   │   │   ├── GlobalVariableCheck_<timestamp>/
│   │   │   │   ├── NewListingCheck_<timestamp>/
│   │   │   ├── ...
│   ├── execution.json
│   └── ground_truth.json
```

1. **`CustomerName/`**: Each customer has a dedicated folder.  
2. **`modules/`**: Contains cloned Git repositories.  
3. **`checks/`**: Contains patch files (diffs) and JSON logs from the checks performed.  
4. **`execution.json`**: Tracks the proposals processed in the last run.  
5. **`ground_truth.json`**: Core configuration defining the official repositories and providers.

---

## License

Quorum is licensed under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/Certora/Quorum).

## Acknowledgments

- Special thanks to all contributors and the open-source community for their support.

---

**Happy Auditing!** If you have any questions or run into issues, please don’t hesitate to create a GitHub issue or open a discussion.
