# Quorum/entry_points/quorum_cli.py

import argparse
from pydantic import BaseModel
from typing import Callable

import Quorum.entry_points.cli_arguments as cli_args
from Quorum.entry_points.implementations.check_proposal import run_single
from Quorum.entry_points.implementations.check_proposal_config import run_config
from Quorum.entry_points.implementations.check_proposal_id import run_proposal_id
from Quorum.entry_points.implementations.create_report import run_create_report
from Quorum.entry_points.implementations.ipfs_validator import run_ipfs_validator
from Quorum.entry_points.implementations.setup_quorum import run_setup_quorum


class Command(BaseModel):
    name: str
    help: str
    arguments: list[cli_args.Argument]
    func: Callable[[argparse.Namespace], None]


COMMAND_REGISTRY = [
    Command(
        name="validate-address",
        help="Run a single payload proposal check.",
        arguments=[
            cli_args.CUSTOMER_ARGUMENT,
            cli_args.CHAIN_ARGUMENT,
            cli_args.PROPOSAL_ADDRESS_ARGUMENT
        ],
        func=run_single
    ),
    Command(
        name="validate-batch",
        help="Run a batch check from a JSON config file.",
        arguments=[cli_args.CONFIG_ARGUMENT],
        func=run_config
    ),
    Command(
        name="validate-by-id",
        help="Check proposals by proposal ID.",
        arguments=[
            cli_args.CUSTOMER_ARGUMENT,
            cli_args.PROPOSAL_ID_ARGUMENT
        ],
        func=run_proposal_id
    ),
    Command(
        name="create-report",
        help="Generate a proposal report.",
        arguments=[
            cli_args.PROPOSAL_ID_ARGUMENT,
            cli_args.TEMPLATE_ARGUMENT,
            cli_args.GENERATE_REPORT_PATH_ARGUMENT
        ],
        func=run_create_report
    ),
    Command(
        name="validate-ipfs",
        help="Compare IPFS content with a proposal's payload.",
        arguments=[
            cli_args.PROPOSAL_ID_ARGUMENT,
            cli_args.CHAIN_ARGUMENT,
            cli_args.PROPOSAL_ADDRESS_ARGUMENT,
            cli_args.PROMPT_TEMPLATES_ARGUMENT
        ],
        func=run_ipfs_validator
    ),
    Command(
        name="setup",
        help="Initial Quorum environment setup.",
        arguments=[cli_args.WORKING_DIR_ARGUMENT],
        func=run_setup_quorum
    )
]


def add_arguments(parser: argparse.ArgumentParser, arguments: list[cli_args.Argument]) -> None:
    """
    Helper function to add arguments to a parser.

    Args:
        parser (argparse.ArgumentParser): The parser or subparser to add arguments to.
        arguments (List[Argument]): A list of Argument instances to add.
    """
    for arg in arguments:
        arg_dict = arg.model_dump()
        name = arg_dict.pop("name")
        parser.add_argument(name, **arg_dict)


def main():
    parser = argparse.ArgumentParser(
        prog="Quorum",
        description="CLI tool for validating and analyzing blockchain governance proposals, including payload verification, IPFS content validation, and report generation."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)


    # Iterate over the registry to add subcommands
    for subcmd in COMMAND_REGISTRY:
        subparser = subparsers.add_parser(
            subcmd.name,
            help=subcmd.help
        )
        add_arguments(subparser, subcmd.arguments)
        subparser.set_defaults(func=subcmd.func)

    args = parser.parse_args()

    # Dispatch to the appropriate function
    args.func(args)


if __name__ == "__main__":
    main()