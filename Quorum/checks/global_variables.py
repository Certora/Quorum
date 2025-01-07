from pathlib import Path

from Quorum.checks.check import Check
from Quorum.apis.block_explorers.source_code import SourceCode
import Quorum.utils.pretty_printer as pp


class GlobalVariableCheck(Check):
    """
    A class that performs a check on global variables within Solidity contracts.

    This class checks if global variables in source codes files are either constant or immutable.
    """

    def check_global_variables(self) -> None:
        """
        Checks global variables in the source code to ensure they are either constant or immutable.

        This method parses the Solidity source code and checks for variables that do not meet the constant
        or immutable criteria.
        """
        source_code_to_violated_variables = {}
        for source_code in self.source_codes:
            violated_variables = self.__check_const(source_code)
            violated_variables = self.__check_immutable(violated_variables, source_code.file_content)

            if violated_variables:
                source_code_to_violated_variables[source_code.file_name] = violated_variables
        
        self.__process_results(source_code_to_violated_variables)

    def __check_const(self, source_code: SourceCode) -> list[dict]:
        """
        Checks a source code for variables that are not declared as constant.

        Args:
            source_code (SourceCode): The Solidity source code obj.

        Returns:
            list[dict]: A list of AST nodes representing variables that are not constant.
        """
        state_variables = source_code.get_state_variables()
        if state_variables:
            return [
                v for v in state_variables.values() 
                if not v.get("constant", False)
            ]
        return []

    def __check_immutable(self, variables: list[dict], source_code: list[str]) -> list[dict]:
        """
        Checks a list of variables to ensure they are declared as immutable in the source code.

        This method searches the source code to verify that the variables are declared with the 'immutable' keyword.

        Args:
            variables (list[dict]): A list of AST nodes representing variables.
            source_code (list[str]): The Solidity source code lines.

        Returns:
            list[dict]: A list of AST nodes representing variables that are not immutable.
        """
        return [v for v in variables if v.get("mutability") != "immutable"]

    def __process_results(self, source_code_to_violated_variables: dict[str, list[dict]]):
        """
        Processes the results of the global variable checks and prints them to the console.

        This method logs the results of the global variable check, including any violations found.

        Args:
            source_code_to_violated_variables (dict[str, list[dict]]): A dictionary mapping file names
                                                                       to lists of violated variables.
        """
        if not source_code_to_violated_variables:
            pp.pprint('All global variables are constant or immutable.', pp.Colors.SUCCESS)
            return
        
        msg = ("Some global variables aren't constant or immutable. A storage collision may occur!\n"
               f'The following variables found to be storage variables: ')
        i = 1
        for file_name, violated_variables in source_code_to_violated_variables.items():
            for var in violated_variables:
                msg += f"\t{i}. File {file_name}: {var['name']}"
                i += 1
            self._write_to_file(Path(file_name).stem.removesuffix('.sol'), violated_variables)
        pp.pprint(msg, pp.Colors.FAILURE)
       