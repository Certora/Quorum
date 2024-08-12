import re
import json
from solidity_parser import parser
from solidity_parser.parser import Node

from ProposalTools.API.api_manager import SourceCode
from ProposalTools.Checks.check import Check
import ProposalTools.Utils.pretty_printer as pp


class GlobalVariableCheck(Check):
    """
    A class that performs a check on global variables within Solidity contracts.

    This class checks if global variables in source codes files are either constant or immutable.
    """

    def __init__(self, customer: str, proposal_address: str, source_codes: list[SourceCode]):
        """
        Initialize the GlobalVariableCheck object.

        Args:
            customer (str): The customer name or identifier.
            proposal_address (str): The Ethereum proposal address.
            source_codes (list[SourceCode]): A list of SourceCode objects.
        """
        super().__init__(customer, proposal_address)
        self.source_codes = source_codes

    def execute_check(self) -> dict[str, list[Node]]:
        """
        Execute the global variable check to ensure they are either constant or immutable.

        This method checks the global variables in the missing files and processes the results.

        Returns:
            dict[str, list[Node]]: A dictionary mapping file names to lists of violated variable nodes.
        """
        source_code_to_violated_variables = self.__check_global_variables()

        self.__process_results(source_code_to_violated_variables)
        return source_code_to_violated_variables

    def get_check_name(self) -> str:
        """
        Get the name of the check.

        This name is used for naming folders or files associated with the check.

        Returns:
            str: The name of the check, "global_check".
        """
        return "global_check"

    def __check_global_variables(self) -> dict[str, list[Node]]:
        """
        Checks global variables in the source code to ensure they are either constant or immutable.

        This method parses the Solidity source code and checks for variables that do not meet the constant
        or immutable criteria.

        Returns:
            dict[str, list[Node]]: A dictionary mapping file names to lists of violated variable nodes.
        """
        source_code_to_violated_variables = {}
        for source_code in self.source_codes:
            source_code_str = "\n".join(source_code.file_content)
            ast = parser.parse(source_code_str)

            violated_variables = self.__check_const(ast)
            violated_variables = self.__check_immutable(violated_variables, source_code.file_content)

            if violated_variables:
                source_code_to_violated_variables[source_code.file_name] = violated_variables

        return source_code_to_violated_variables

    def __check_const(self, ast_node: Node) -> list[Node]:
        """
        Recursively checks the AST for state variables that are not declared as constant.

        This method traverses the AST to identify state variables that lack the 'constant' declaration.

        Args:
            ast_node (Node): The root AST node to start checking from.

        Returns:
            list[Node]: A list of AST nodes representing variables that are not constant.
        """
        violated_variables = []

        if ast_node.get('type') == 'StateVariableDeclaration':
            for variable in ast_node.get('variables', []):
                if not variable.get('isDeclaredConst', False):
                    violated_variables.append(variable)

        for child in ast_node.values():
            if isinstance(child, dict):
                violated_variables.extend(self.__check_const(child))
            elif isinstance(child, list):
                for item in child:
                    if isinstance(item, dict):
                        violated_variables.extend(self.__check_const(item))

        return violated_variables

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
