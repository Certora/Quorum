import solcx
from dataclasses import dataclass
from pathlib import Path
from enum import StrEnum

import Quorum.utils.pretty_printer as pp


# Install the latest version of Solidity compiler.
solc_version = solcx.get_compilable_solc_versions()[0]
solcx.install_solc(solc_version)
solcx.set_solc_version(solc_version)


class ASTOption(StrEnum):
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
        self._functions = None
        self._state_variables = None
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
            pp.pprint(f"Error parsing source code for {self.file_name}: {e}\n"
                            f"Some of the checks will not apply to this contract!!!",
                            pp.Colors.FAILURE)
        finally:
            tmp_path.unlink()
    
    def __extract_nodes(self, ast: dict, node_type: ASTOption) -> dict:
        nodes = {}
        visited = set()
        for node in ast['nodes']:
            if node['id'] in visited:
                continue
            visited.add(node['id'])
            if node['nodeType'] == node_type:
                name = node['name']
                nodes[name] = node
            elif 'nodes' in node:
                nodes.update(self.__extract_nodes(node, node_type))
        return nodes

    def get_functions(self) -> dict:
        """
        Retrieves the functions from the Solidity contract.

        Returns:
            (dict): Dictionary of functions or None if not found.
        """
        if not self._functions:
            if self._parsed_contract:
                self._functions = self.__extract_nodes(self._parsed_contract, ASTOption.FUNCTIONS)
        return self._functions

    def get_state_variables(self) -> dict:
        """
        Retrieves the state variables from the Solidity contract.

        Returns:
            (dict): Dictionary of state variables or None if not found.
        """
        if not self._state_variables:
            if self._parsed_contract:
                self._state_variables = self.__extract_nodes(self._parsed_contract, ASTOption.STATE_VARIABLES)
        return self._state_variables
