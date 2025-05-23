# Quorum/entry_points/quorum_cli.py

import argparse
from collections.abc import Callable

import argcomplete
from pydantic import BaseModel

import quorum
import quorum.entry_points.cli_arguments as cli_args
from quorum.entry_points.implementations.check_local_proposal import run_local_proposal
from quorum.entry_points.implementations.check_proposal import run_single
from quorum.entry_points.implementations.check_proposal_config import run_config
from quorum.entry_points.implementations.check_proposal_id import run_proposal_id
from quorum.entry_points.implementations.create_report import run_create_report
from quorum.entry_points.implementations.ipfs_validator import run_ipfs_validator
from quorum.entry_points.implementations.setup_quorum import run_setup_quorum


class Command(BaseModel):
    name: str
    help: str
    arguments: list[cli_args.Argument]
    func: Callable[[argparse.Namespace], None]


COMMAND_REGISTRY = [
    Command(
        name="setup",
        help="Sets up Quorum environment for quick start.",
        arguments=[cli_args.WORKING_DIR_ARGUMENT],
        func=run_setup_quorum,
    ),
    Command(
        name="validate-address",
        help="Validate a single on-chain payload by address.",
        arguments=[
            cli_args.PROTOCOL_NAME_ARGUMENT,
            cli_args.CHAIN_ARGUMENT,
            cli_args.PAYLOAD_ADDRESS_ARGUMENT,
        ],
        func=run_single,
    ),
    Command(
        name="validate-batch",
        help="Run a batch check from a JSON config file.",
        arguments=[cli_args.CONFIG_ARGUMENT],
        func=run_config,
    ),
    Command(
        name="validate-by-id",
        help="Validate a single on-chain proposal by passing the protocol name and id.",
        arguments=[cli_args.PROTOCOL_NAME_ARGUMENT, cli_args.PROPOSAL_ID_ARGUMENT],
        func=run_proposal_id,
    ),
    Command(
        name="validate-ipfs",
        help="Compare IPFS content with a proposal's payload.",
        arguments=[
            cli_args.PROPOSAL_ID_ARGUMENT,
            cli_args.CHAIN_ARGUMENT,
            cli_args.PAYLOAD_ADDRESS_ARGUMENT,
            cli_args.CONTRACT_NAME_ARGUMENT,
            cli_args.PROMPT_TEMPLATES_ARGUMENT,
        ],
        func=run_ipfs_validator,
    ),
    Command(
        name="generate-report",
        help="Generates a proposal report based on provided JINJA2 template.",
        arguments=[
            cli_args.PROPOSAL_ID_ARGUMENT,
            cli_args.TEMPLATE_ARGUMENT,
            cli_args.OUTPUT_PATH_ARGUMENT,
        ],
        func=run_create_report,
    ),
    Command(
        name="validate-local-payload",
        help="validate a single local payload",
        arguments=[
            cli_args.PROTOCOL_NAME_ARGUMENT,
            cli_args.CHAIN_ARGUMENT,
            cli_args.FORGE_ROOT_PATH_ARGUMENT,
            cli_args.CONTRACT_PROPOSAL_PATH_ARGUMENT,
        ],
        func=run_local_proposal,
    ),
]


def add_arguments(
    parser: argparse.ArgumentParser, arguments: list[cli_args.Argument]
) -> None:
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
        description="CLI tool for validating and analyzing blockchain governance proposals, including payload verification, IPFS content validation, and report generation.",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {quorum.__version__}"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Iterate over the registry to add subcommands
    for subcmd in COMMAND_REGISTRY:
        subparser = subparsers.add_parser(subcmd.name, help=subcmd.help)
        add_arguments(subparser, subcmd.arguments)
        subparser.set_defaults(func=subcmd.func)

    argcomplete.autocomplete(parser)

    args = parser.parse_args()

    # Dispatch to the appropriate function
    args.func(args)


if __name__ == "__main__":
    main()
