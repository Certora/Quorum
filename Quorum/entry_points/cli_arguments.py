from pydantic import BaseModel
from typing import Any
from pathlib import Path

from Quorum.utils.chain_enum import Chain
import Quorum.utils.arg_validations as arg_valid


class Argument(BaseModel):
    name: str
    type: Any
    required: bool
    help: str
    default: Any | None = None
    nargs: str | None = None


CUSTOMER_ARGUMENT = Argument(
    name='--customer',
    type=str,
    required=True,
    help="Customer name or identifier."
)


CHAIN_ARGUMENT = Argument(
    name='--chain',
    type=Chain,
    required=True,
    help="Blockchain chain to target."
)


PROPOSAL_ADDRESS_ARGUMENT = Argument(
    name='--proposal_address',
    type=arg_valid.validate_address,
    required=True,
    help="Ethereum proposal address."
)


PROPOSAL_ID_ARGUMENT = Argument(
    name='--proposal_id',
    type=int,
    required=True,
    help="ID of the proposal."
)


CONFIG_ARGUMENT = Argument(
    name='--config',
    type=arg_valid.load_config,
    required=True,
    help="Path to the JSON configuration file."
)


TEMPLATE_ARGUMENT = Argument(
    name='--template',
    type=Path,
    required=False,
    help="Path to the Jinja2 template file.",
    default=Path(__file__).parent.parent / 'auto_report/AaveReportTemplate.md.j2'
)


GENERATE_REPORT_PATH_ARGUMENT = Argument(
    name='--generate_report_path',
    type=Path,
    required=False,
    help="Path to save the generated report."
)


PROMPT_TEMPLATES_ARGUMENT = Argument(
    name='--prompt_templates',
    type=str,
    required=False,
    help="Jinja templates for prompting the LLM.",
    default=['ipfs_validation_prompt_part1.j2', "ipfs_validation_prompt_part2.j2"],
    nargs="+"
)


WORKING_DIR_ARGUMENT = Argument(
    name='--working_dir',
    type=Path,
    required=False,
    help="Where to create the Quorum project.",
    default=Path.cwd() / 'quorum_project'
)
