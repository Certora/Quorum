from pathlib import Path
from typing import Any

from pydantic import BaseModel

import quorum.utils.arg_validations as arg_valid
from quorum.utils.chain_enum import Chain


def to_lower_str(value: str) -> str:
    """Convert the input string to lower case."""
    if not isinstance(value, str):
        raise ValueError(f"Expected a string, but got {value} of type {type(value)}")
    return value.lower()


class Argument(BaseModel):
    name: str
    type: Any
    required: bool
    help: str
    default: Any | None = None
    nargs: str | None = None


PROTOCOL_NAME_ARGUMENT = Argument(
    name="--protocol-name",
    type=to_lower_str,  # Normalize protocol name to lower case
    required=True,
    help="Protocol name or identifier.",
)


CHAIN_ARGUMENT = Argument(
    name="--chain",
    type=Chain,  # Case-insensitive chain parsing
    required=True,
    help="Blockchain to target.",
)


PAYLOAD_ADDRESS_ARGUMENT = Argument(
    name="--payload-address",
    type=lambda s: arg_valid.validate_address(
        s
    ).lower(),  # Normalize address to lower-case
    required=True,
    help="On-chain payload address.",
)


PROPOSAL_ID_ARGUMENT = Argument(
    name="--proposal-id",
    type=int,
    required=True,
    help="Identifier of the proposal.",
)


CONFIG_ARGUMENT = Argument(
    name="--config",
    type=arg_valid.load_config,
    required=True,
    help="Path to the Json config file.",
)


TEMPLATE_ARGUMENT = Argument(
    name="--template",
    type=Path,
    required=False,
    help="Path to a Jinja2 template file that defines the output report format.",
    default=Path(__file__).parent.parent / "auto_report/AaveReportTemplate.md.j2",
)


OUTPUT_PATH_ARGUMENT = Argument(
    name="--output-path",
    type=Path,
    required=False,
    help="The path to which the report is saved.",
)


PROMPT_TEMPLATES_ARGUMENT = Argument(
    name="--prompt-templates",
    type=str,
    required=False,
    help="Jinja templates for prompting the LLM.",
    default=["ipfs_validation_prompt.j2"],
    nargs="+",
)

WORKING_DIR_ARGUMENT = Argument(
    name="--working-dir",
    type=Path,
    required=False,
    help="Specifies the path in which the project will be created. \n Note that all validations will have to run from this directory!",
    default=Path.cwd() / "quorum_project",
)


FORGE_ROOT_PATH_ARGUMENT = Argument(
    name="--forge-root-path",
    type=Path,
    required=True,
    help="The path to where the command forge build --contracts <contract_proposal_path> is working.",
)


CONTRACT_PROPOSAL_PATH_ARGUMENT = Argument(
    name="--contract-proposal-path",
    type=Path,
    required=True,
    help="The path to the contract proposal file.",
)
