# Quorum Templates Guide

This guide provides instructions on how to fill out the various template files in the Quorum project.

## ground_truth.json

This file contains the ground truth data for different protocols. Each protocol has its own section with the following fields:

- `dev_repos`: A list of URLs to the development repositories.
- `review_repo`: The URL to the review repository.
- `price_feed_providers`: A list of price feed providers.
- `token_validation_providers`: A list of token validation providers.

### Example
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

## execution.json

This file contains the execution details for different protocols and networks. For each protocol, you need to specify the proposal addresses for various networks.

### Instructions
- Replace `<protocol_name>` with the name of the protocol as specified in `ground_truth.json`.
- Fill in the proposal addresses for each network.

### Example
```jsonc
{
    "Aave": {
        "Ethereum": {
            "Proposals": ["0x..."] // Insert Ethereum proposals address here
        },
        "Arbitrum": {
            "Proposals": ["0x..."] // Insert Arbitrum proposals address here
        },
        // ...other networks...
    }
}
```

## .env

This file contains environment variables that needs to be set for the project to run.
fill in the required values.

### Instructions
- `ETHSCAN_API_KEY`: Your Etherscan API key.
- `ANTHROPIC_API_KEY`: Your Anthropic API key.
- `QUORUM_PATH`: The path to your Quorum directory.

### Example
```bash
export ETHSCAN_API_KEY="your_etherscan_api_key"
export ANTHROPIC_API_KEY="your_anthropic_api_key"
export QUORUM_PATH="path_to_your_quorum_directory"
```

## Summary

1. Fill in `ground_truth.json` with the appropriate data for each protocol.
2. Update `execution.json` with the proposal addresses for each network.
3. Set the required environment variables at `.env`.

By following these instructions, you will ensure Quorum is correctly configured and ready to use.
