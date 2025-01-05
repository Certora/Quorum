from enum import StrEnum


SEPARATOR_LINE = '\n' + '-' * 110 + '\n'


class Colors(StrEnum):
    SUCCESS = '\033[92m'
    FAILURE = '\033[91m'
    WARNING = '\033[93m'
    INFO = ''
    RESET = '\033[0m'


def pprint(message: str, status: Colors, is_heading: bool = False):
    s = status + message + Colors.RESET
    if is_heading:
        s += '\n' + '-' * len(message)
    print(s)
