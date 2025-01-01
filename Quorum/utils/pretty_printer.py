from enum import StrEnum

class Colors(StrEnum):
    SUCCESS = '\033[92m'
    FAILURE = '\033[91m'
    WARNING = '\033[93m'
    INFO = ''
    RESET = '\033[0m'

def pprint(message: str, status: Colors):
    separator_line = status + '-' * 80 + Colors.RESET
    print(separator_line)
    print(status + message + Colors.RESET)
    print(separator_line)
