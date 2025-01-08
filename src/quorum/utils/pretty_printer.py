from enum import StrEnum
from typing import Optional


SEPARATOR_LINE = '\n' + '-' * 110 + '\n'


class Heading(StrEnum):
    HEADING_1 = '='
    HEADING_2 = '-'
    HEADING_3 = '.'


class Colors(StrEnum):
    SUCCESS = '\033[92m'
    FAILURE = '\033[91m'
    WARNING = '\033[93m'
    INFO = ''
    RESET = '\033[0m'


def pprint(message: object, status: Colors, heading: Optional[Heading]=None):
    s = status + str(message) + Colors.RESET
    if heading:
        s += '\n' + heading * len(message) + '\n'
    print(s)
