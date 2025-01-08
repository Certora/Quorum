# Quorum/entry_points/quorum_cli.py

import argparse
from pydantic import BaseModel

import Quorum.entry_points.cli_arguments as cli_args


class Command(BaseModel):
    name: str
    help: str
    arguments: list[cli_args.Argument]


COMMAND_REGISTRY = [
    Command(
        name="generate-report",
        help="Generates a proposal report based on provided JINJA2 template.",
        arguments=[
            cli_args.PROPOSAL_ID_ARGUMENT,
            cli_args.TEMPLATE_ARGUMENT,
            cli_args.OUTPUT_PATH_ARGUMENT
        ],
    ),
    Command(
        name="setup",
        help="Sets up Quorum environment for quick start.",
        arguments=[cli_args.WORKING_DIR_ARGUMENT],
    ),
    Command(
        name="validate-address",
        help="Validate a single on-chain payload by address.",
        arguments=[
            cli_args.PROTOCOL_NAME_ARGUMENT,
            cli_args.CHAIN_ARGUMENT,
            cli_args.PAYLOAD_ADDRESS_ARGUMENT
        ],
    ),
    Command(
        name="validate-batch",
        help="Run a batch check from a JSON config file.",
        arguments=[cli_args.CONFIG_ARGUMENT]
    ),
    Command(
        name="validate-by-id",
        help="Validate a single on-chain proposal by passing the protocol name and id.",
        arguments=[
            cli_args.PROTOCOL_NAME_ARGUMENT,
            cli_args.PROPOSAL_ID_ARGUMENT
        ]
    ),
    Command(
        name="create-report",
        help="Generate a proposal report.",
        arguments=[
            cli_args.PROPOSAL_ID_ARGUMENT,
            cli_args.TEMPLATE_ARGUMENT,
            cli_args.OUTPUT_PATH_ARGUMENT
        ]
    ),
    Command(
        name="validate-ipfs",
        help="Compare IPFS content with a proposal's payload.",
        arguments=[
            cli_args.PROPOSAL_ID_ARGUMENT,
            cli_args.CHAIN_ARGUMENT,
            cli_args.PAYLOAD_ADDRESS_ARGUMENT,
            cli_args.PROMPT_TEMPLATES_ARGUMENT
        ]
    ),
    Command(
        name="setup",
        help="Initial Quorum environment setup.",
        arguments=[cli_args.WORKING_DIR_ARGUMENT]
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

        if subcmd.name == "validate-address":
            def run(args):
                from Quorum.entry_points.implementations.check_proposal import run_single
                run_single(args)
            subparser.set_defaults(func=run)
        elif subcmd.name == "validate-batch":
            def run(args):
                from Quorum.entry_points.implementations.check_proposal_config import run_config
                run_config(args)
            subparser.set_defaults(func=run)
        elif subcmd.name == "validate-by-id":
            def run(args):
                from Quorum.entry_points.implementations.check_proposal_id import run_proposal_id
                run_proposal_id(args)
            subparser.set_defaults(func=run)
        elif subcmd.name == "create-report":
            def run(args):
                from Quorum.entry_points.implementations.create_report import run_create_report
                run_create_report(args)
            subparser.set_defaults(func=run)
        elif subcmd.name == "validate-ipfs":
            def run(args):
                from Quorum.entry_points.implementations.ipfs_validator import run_ipfs_validator
                run_ipfs_validator(args)
            subparser.set_defaults(func=run)
        elif subcmd.name == "setup":
            def run(args):
                from Quorum.entry_points.implementations.setup_quorum import run_setup_quorum
                run_setup_quorum(args)
            subparser.set_defaults(func=run)

    args = parser.parse_args()

    # Dispatch to the appropriate function
    args.func(args)


if __name__ == "__main__":
    main()
