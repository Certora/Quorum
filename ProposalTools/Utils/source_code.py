from solidity_parser import parser
from dataclasses import dataclass

import ProposalTools.Utils.pretty_printer as pp


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

        try:
            ast = parser.parse(source_code_str)
            ast_obj = parser.objectify(ast)
            contract_name = ast_obj._current_contract.name
            self._parsed_contract = ast_obj.contracts[contract_name]
        except Exception as e:
            pp.pretty_print(f"Error parsing source code for {self.file_name}: {e}\n"
                            f"Some of the checks will not apply to this contract!!!",
                            pp.Colors.FAILURE)

    def get_constructor(self) -> dict | None:
        """
        Retrieves the constructor information from the Solidity contract.

        Returns:
            (dict | None): Constructor information or None if not found.
        """
        if self._parsed_contract:
            return self._parsed_contract.constructor
        return None

    def get_dependencies(self) -> list | None:
        """
        Retrieves the dependencies from the Solidity contract.

        Returns:
            (list | None): List of dependencies or None if not found.
        """
        if self._parsed_contract:
            return self._parsed_contract.dependencies
        return None

    def get_enums(self) -> list | None:
        """
        Retrieves the enums from the Solidity contract.

        Returns:
            (list | None): List of enums or None if not found.
        """
        if self._parsed_contract:
            return self._parsed_contract.enums
        return None

    def get_events(self) -> list | None:
        """
        Retrieves the events from the Solidity contract.

        Returns:
            (list | None): List of events or None if not found.
        """
        if self._parsed_contract:
            return self._parsed_contract.events
        return None

    def get_functions(self) -> dict | None:
        """
        Retrieves the functions from the Solidity contract.

        Returns:
            (dict | None): List of functions or None if not found.
        """
        if self._parsed_contract:
            return self._parsed_contract.functions
        return None

    def get_inherited_names(self) -> list | None:
        """
        Retrieves the inherited names from the Solidity contract.

        Returns:
            (list | None): List of inherited names or None if not found.
        """
        if self._parsed_contract:
            return self._parsed_contract.inherited_names
        return None

    def get_mappings(self) -> list | None:
        """
        Retrieves the mappings from the Solidity contract.

        Returns:
            (list | None): List of mappings or None if not found.
        """
        if self._parsed_contract:
            return self._parsed_contract.mappings
        return None

    def get_modifiers(self) -> list | None:
        """
        Retrieves the modifiers from the Solidity contract.

        Returns:
            (list | None): List of modifiers or None if not found.
        """
        if self._parsed_contract:
            return self._parsed_contract.modifiers
        return None

    def get_name(self) -> str | None:
        """
        Retrieves the contract name.

        Returns:
            (str | None): Contract name or None if not found.
        """
        if self._parsed_contract:
            return self._parsed_contract.name
        return None

    def get_state_variables(self) -> dict | None:
        """
        Retrieves the state variables from the Solidity contract.

        Returns:
            (dict | None): Dictionary of state variables or None if not found.
        """
        if self._parsed_contract:
            return self._parsed_contract.stateVars
        return None

    def get_structs(self) -> list | None:
        """
        Retrieves the structs from the Solidity contract.

        Returns:
            (list | None): List of structs or None if not found.
        """
        if self._parsed_contract:
            return self._parsed_contract.structs
        return None
