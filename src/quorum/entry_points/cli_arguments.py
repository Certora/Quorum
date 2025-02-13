from pathlib import Path
from typing import Any

from pydantic import BaseModel

import quorum.utils.arg_validations as arg_valid
from quorum.utils.chain_enum import Chain


def to_lower_str(value: str) -> str:
    """Convert the input string to lower case."""
    return value.lower()


def parse_chain_case_insensitive(value: str) -> Chain:
    """
    Parse a blockchain chain input in a case-insensitive manner.
    Returns the Chain enum member matching the input, regardless of case.
    """
    for chain in Chain:
        if chain.value.lower() == value.lower():
            return chain
    raise ValueError(f"Invalid chain: {value}")


class Argument(BaseModel):
    name: list[str]
    type: Any
    required: bool
    help: str
    default: Any | None = None
    nargs: str | None = None


PROTOCOL_NAME_ARGUMENT = Argument(
    name=["--protocol-name", "--protocol_name"],
    type=to_lower_str,  # Normalize protocol name to lower case
    required=True,
    help="Protocol name or identifier.",
)

CHAIN_ARGUMENT = Argument(
    name=["--chain"],
    type=parse_chain_case_insensitive,  # Case-insensitive chain parsing
    required=True,
    help="Blockchain to target.",
)

PAYLOAD_ADDRESS_ARGUMENT = Argument(
    name=["--payload-address", "--payload_address"],
    type=lambda s: arg_valid.validate_address(
        s
    ).lower(),  # Normalize address to lower-case
    required=True,
    help="On-chain payload address.",
)

PROPOSAL_ID_ARGUMENT = Argument(
    name=["--proposal-id", "--proposal_id"],
    type=int,
    required=True,
    help="Identifier of the proposal.",
)

CONFIG_ARGUMENT = Argument(
    name=["--config"],
    type=arg_valid.load_config,
    required=True,
    help="Path to the Json config file.",
)

TEMPLATE_ARGUMENT = Argument(
    name=["--template"],
    type=Path,
    required=False,
    help="Path to a Jinja2 template file that defines the output report format.",
    default=Path(__file__).parent.parent / "auto_report/AaveReportTemplate.md.j2",
)

OUTPUT_PATH_ARGUMENT = Argument(
    name=["--output-path", "--output_path"],
    type=Path,
    required=False,
    help="The path to which the report is saved.",
)

PROMPT_TEMPLATES_ARGUMENT = Argument(
    name=["--prompt-templates", "--prompt_templates"],
    type=str,
    required=False,
    help="Jinja templates for prompting the LLM.",
    default=["ipfs_validation_prompt_part1.j2", "ipfs_validation_prompt_part2.j2"],
    nargs="+",
)

WORKING_DIR_ARGUMENT = Argument(
    name=["--working-dir", "--working_dir"],
    type=Path,
    required=False,
    help="Specifies the path in which the project will be created. \n Note that all validations will have to run from this directory!",
    default=Path.cwd() / "quorum_project",
)
