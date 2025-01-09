# Quorum Developer Guide

Welcome to the **Quorum** project! This guide helps developers get set up with the local environment, including:

1. Installing and configuring **Poetry** for dependency management  
2. Using **direnv** for automatic environment activation  
3. Running **Quorum** commands and verifying everything is correct  

## 1. Requirements

1. **Python** version `>=3.11,<4.0`
2. **Poetry** version `1.8+` (recommended)
3. **direnv** (optional but highly recommended for convenience)
4. (Optional) A local `.env` file for secret variables, personal overrides, etc.

## 2. Project Structure

A quick look at our relevant files and directories:

```
.
├── LICENSE
├── MANIFEST.in
├── Makefile
├── README.md
├── poetry.lock
├── pyproject.toml
├── .envrc                 # direnv config file
├── .env.example           # Example environment variables
└── src
    └── quorum            # Project code
       ├── __init__.py
       ├── entry_points
       ├── ...
```

## 3. Setting up the Project Environment

### 3.1 Install or Update Poetry

If you haven’t installed Poetry (or have an older version), do so with:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Verify the version:

```bash
poetry --version
```

### 3.2 Configure direnv (Optional but Recommended)

**direnv** is a tool that automatically loads/unloads environment variables when entering/leaving directories. We use it to:

- **Auto-activate** the correct Poetry virtual environment
- Optionally load environment variables from a `.env` file

#### 3.2.1 Install direnv

On **macOS** (Homebrew):

```bash
brew install direnv
```

On **Linux** (e.g., Ubuntu/Debian):

```bash
sudo apt-get update
sudo apt-get install direnv
```

#### 3.2.2 Integrate with Shell

For **bash** or **zsh**, add this to your `~/.bashrc`, `~/.zshrc`, etc.:

```bash
eval "$(direnv hook bash)"   # or zsh, fish, etc.
```

Then run:

```bash
direnv allow
```

So every time you `cd` into the project folder, your environment is **automatically loaded** 
And fully configured according to your .env and all packages already installed.

### 3.3 Install Dependencies

#### 3.3.1 Using Poetry

Once inside your project directory (and optionally, after `direnv allow`), run:

```bash
poetry install
```

This installs all dependencies (including dev dependencies) listed in `pyproject.toml`.

## 4. Running Quorum Locally

We provide a CLI **`quorum`**. Once your environment is active, you can run:

```bash
poetry run quorum --help
```

Or, if you’re using **direnv** or in the Poetry shell:

```bash
quorum --help
```

### 4.1 Example Commands

- **Single Payload Validation**:
  ```bash
  quorum validate-address --protocol-name Aave --chain Ethereum --payload-address 0xAD6...
  ```
- **Batch Validation** (config-based):
  ```bash
  quorum validate-batch --config path/to/config.json
  ```
- **Proposal ID Check**:
  ```bash
  quorum validate-by-id --proposal-id 137 --protocol-name Aave
  ```
- **IPFS Validation**:
  ```bash
  quorum validate-ipfs --proposal-id 20 --chain Scroll --payload-address 0x2B25cb...
  ```
- **Generate Report**:
  ```bash
  quorum generate-report --proposal_id 137
  ```

## 5. Developing with Ruff & Pre-Commit

**Ruff** is our linter and auto-fixer. **pre-commit** runs Ruff automatically before each commit if you have it configured. Typical usage:

```bash
# Run ruff checks manually:
poetry run ruff check src

# Auto-fix issues:
poetry run ruff check src --fix
```

If you have a `.pre-commit-config.yaml` with a ruff hook, you can do:

```bash
pre-commit install
pre-commit run --all-files
```

## 6. Additional Environment Variables (Optional)

If you want to store secrets like `ETHSCAN_API_KEY`, `ANTHROPIC_API_KEY`, etc., do one of the following:

- Put them in a local `.env` file in the project root (which is `.gitignore`d). Example:
  ```bash
  ETHSCAN_API_KEY="abc123"
  ANTHROPIC_API_KEY="xxx"
  ```
  Then add `dotenv 2>/dev/null` in your `.envrc`.
- Or set them in your shell profile (`~/.bashrc`, `~/.zshrc`, etc.).
- Or pass them directly in your CI environment.

---

## That’s It!

You are now set up with:

- **Poetry** for dependency and environment management
- **direnv** for auto-activating your environment
- **Ruff** linting with optional pre-commit hooks
- **Quorum** CLI commands to run local validations and generate reports
