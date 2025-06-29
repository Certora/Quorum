from enum import StrEnum

SEPARATOR_LINE = "\n" + "-" * 110 + "\n"


class Heading(StrEnum):
    HEADING_1 = "="
    HEADING_2 = "-"
    HEADING_3 = "."


class Colors(StrEnum):
    SUCCESS = "\033[92m"
    FAILURE = "\033[91m"
    WARNING = "\033[93m"
    INFO = ""
    RESET = "\033[0m"


def pprint(message: object, status: Colors, heading: Heading | str | None = None):
    s = status + str(message) + Colors.RESET
    if heading:
        if isinstance(heading, str):
            # Custom heading string with underline
            s += "\n" + heading + "\n" + "=" * len(heading) + "\n"
        else:
            # Heading enum value - create underline based on message length
            s += "\n" + heading * len(str(message)) + "\n"
    print(s)
