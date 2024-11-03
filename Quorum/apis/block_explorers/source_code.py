import solcx
from dataclasses import dataclass
from pathlib import Path
from enum import StrEnum

import Quorum.utils.pretty_printer as pp

class ExtractASTOption(StrEnum):
    FUNCTIONS = "FunctionDefinition"
    STATE_VARIABLES = "VariableDeclaration"


@dataclass
class SourceCode:
    """
    Data class representing source code information.
    """
    file_name: str
    file_content: list[str]

    def __post_init__(self):
        self._parsed_contract = None
        self._parse_source_code()

    def _parse_source_code(self) -> None:
        """
        Parses the Solidity source code and stores the contract's AST object.
        """
        source_code_str = "\n".join(self.file_content)
        tmp_path = Path("tmp.sol")

        with open(tmp_path, 'w') as file:
            file.write(source_code_str)

        try:
            contract_ast = solcx.compile_files(tmp_path, output_values=["ast"], stop_after="parsing")
            contract_name = list(contract_ast.keys())[0]
            self._parsed_contract = contract_ast[contract_name]['ast']

        except Exception as e:
            pp.pretty_print(f"Error parsing source code for {self.file_name}: {e}\n"
                            f"Some of the checks will not apply to this contract!!!",
                            pp.Colors.FAILURE)
        finally:
            tmp_path.unlink()
    
    def __extract_nodes(self, ast: dict, node_type: ExtractASTOption) -> list:
        functions = {}
        visited = set()
        for node in ast['nodes']:
            if node['id'] in visited:
                continue
            visited.add(node['id'])
            if node['nodeType'] == node_type:
                name = node['name']
                functions[name] = node
            elif 'nodes' in node:
                functions.update(self.__extract_nodes(node, node_type))
        return functions

    def get_functions(self) -> dict | None:
        """
        Retrieves the functions from the Solidity contract.

        Returns:
            (dict | None): Dictionary of functions or None if not found.
        """
        if self._parsed_contract:
            return self.__extract_nodes(self._parsed_contract, ExtractASTOption.FUNCTIONS)
        return None

    def get_state_variables(self) -> dict | None:
        """
        Retrieves the state variables from the Solidity contract.

        Returns:
            (dict | None): Dictionary of state variables or None if not found.
        """
        if self._parsed_contract:
            return self.__extract_nodes(self._parsed_contract, ExtractASTOption.STATE_VARIABLES)
        return None
