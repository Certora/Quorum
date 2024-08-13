import re
import json
from solidity_parser.parser import Node


from ProposalTools.Checks.check import Check
from ProposalTools.Utils.source_code import SourceCode
import ProposalTools.Utils.pretty_printer as pp


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
            violated_variables = self.__check_immutable(violated_variables, source_code)

            if violated_variables:
                source_code_to_violated_variables[source_code.file_name] = violated_variables
        
        self.__process_results(source_code_to_violated_variables)

    def __check_const(self, source_code: SourceCode) -> list[Node]:
        """
        Checks a source code for variables that are not declared as constant.

        Args:
            source_code (SourceCode): The Solidity source code obj.

        Returns:
            list[Node]: A list of AST nodes representing variables that are not constant.
        """
        state_variables = source_code.get_state_variables()
        return [
            v for v in state_variables.values() 
            if not v.get("isDeclaredConst", False)
        ]

    def __check_immutable(self, variables: list[Node], source_code: list[str]) -> list[Node]:
        """
        Checks a list of variables to ensure they are declared as immutable in the source code.

        This method searches the source code to verify that the variables are declared with the 'immutable' keyword.

        Args:
            variables (list[Node]): A list of AST nodes representing variables.
            source_code (list[str]): The Solidity source code lines.

        Returns:
            list[Node]: A list of AST nodes representing variables that are not immutable.
        """
        violated_variables = []

        for variable in variables:
            variable_name = variable.get('name')
            var_type = variable.get('typeName').get('name')
            pattern = rf".*{var_type}.*{variable_name}.*"

            found = False
            for line in source_code:
                if re.search(pattern, line):
                    found = True
                    if "immutable" not in line:
                        violated_variables.append(variable)
                    break

            if not found:
                violated_variables.append(variable)

        return violated_variables

    def __process_results(self, source_code_to_violated_variables: dict[str, list[Node]]):
        """
        Processes the results of the global variable checks and prints them to the console.

        This method logs the results of the global variable check, including any violations found.

        Args:
            source_code_to_violated_variables (dict[str, list[Node]]): A dictionary mapping file names
                                                                       to lists of violated variables.
        """
        if not source_code_to_violated_variables:
            pp.pretty_print("All global variables are constant or immutable.", pp.Colors.SUCCESS)
        else:
            pp.pretty_print("Global variable checks failed:", pp.Colors.FAILURE)
            pp.pretty_print(f"Customer: {self.customer}, Proposal: {self.proposal_address}", pp.Colors.FAILURE)
            for file_name, violated_variables in source_code_to_violated_variables.items():
                file_path = self.check_folder / file_name
                pp.pretty_print(f"File {file_name} contains variables that are not constant or immutable:"
                                f" Violated variables can be found here: {file_path}",
                                pp.Colors.FAILURE)
                with open(file_path, 'a') as f:
                    json.dump(violated_variables, f)
