# IPFS Payload Validation Script

This script compares the payload stored on IPFS for a governance proposal with the actual payload on the blockchain. It automates the process of fetching, validating, and analyzing data using an LLM (Large Language Model) and other APIs.

---

## Features

1. **Blockchain Integration**:
   - Fetches blockchain data via the `ChainAPI` for a specified chain.
   
2. **IPFS Data Retrieval**:
   - Retrieves IPFS data for governance proposals using a scraping approach (temporary).

3. **Prompt Customization**:
   - Supports custom templates for the LLM to validate and compare data.

4. **LLM Integration**:
   - Sends prepared prompts to Anthropic's Claude AI for detailed analysis.

5. **Caching**:
   - Implements caching for IPFS data to optimize performance and minimize redundant requests.

---

## Requirements

### External APIs
Currently only supports Claude.
- **Anthropic Claude**:
  Requires an API key configured as an env variable `ANTHROPIC_API_KEY`.


---


## Usage

Run the script using the command-line interface:

```bash

IPFSValidator --proposal_id <ID> --chain <CHAIN> --proposal_address <ADDRESS> [--prompt_template <TEMPLATE_PATH>]
```

### Arguments
- `--proposal_id` (int): ID of the governance proposal to validate.
- `--chain` (str): Blockchain chain (e.g., `ethereum`).
- `--proposal_address` (str): Ethereum address of the proposal.
- `--prompt_template` (path): Optional custom path to a prompt template.

---

## Workflow

1. **Parse Input Arguments**:
   Validates and processes the provided command-line arguments.

2. **Fetch Blockchain Data**:
   Retrieves source code for the specified proposal address using the blockchain's explorer API.

3. **Fetch IPFS Data**:
   Extracts the IPFS hash for the proposal and fetches the corresponding data.

4. **Prepare Prompts**:
   Constructs prompts using a predefined template, replacing placeholders with actual data.

5. **Analyze Data with LLM**:
   Sends the prompts to Claude AI for analysis and prints the response.

---

## Known Limitations

- **Fragile Scraping**:
  The script currently scrapes Aave's governance UI for IPFS hashes. This approach is not reliable and should be replaced with an API when available.

- **Dependency on External APIs**:
  The script requires access to Anthropic's Claude API and Aave's governance UI.
