from pydantic import BaseModel

from Quorum.checks.check import Check
import Quorum.utils.pretty_printer as pp


class ListingDetails(BaseModel):
    asset: str
    assetSymbol: str = None
    priceFeedAddress: str = None


class FunctionCallDetails(BaseModel):
    pool: str
    asset: str
    asset_seed: str


class NewListingCheck(Check):
    def new_listing_check(self) -> None:
        """
        Checks if the proposal address is a new listing on the blockchain.
        This method retrieves functions from the source codes and checks if there are any new listings.
        If new listings are detected, it handles them accordingly. Otherwise, it prints a message indicating
        no new listings were found.
        """
        functions = self._get_functions_from_source_codes()

        if "newListings" in functions or "newListingsCustom" in functions:
            self._handle_new_listings(functions)
        else:
            pp.pretty_print(f"No new listings detected for {self.proposal_address}", pp.Colors.INFO)

    def _get_functions_from_source_codes(self) -> dict:
        """
        Retrieves functions from the source codes.
        This method iterates over the source codes and collects all functions defined in them.
        Returns:
            dict: A dictionary where keys are function names and values are function nodes.
        """
        functions = {}
        for source_code in self.source_codes:
            functions.update(source_code.get_functions() if source_code.get_functions() else {})
        return functions

    def _handle_new_listings(self, functions: dict) -> None:
        """
        Handles new listings detected in the functions.
        This method extracts listings from the function node and checks for approval and supply calls
        related to the listings. It prints messages indicating the status of these calls.
        Args:
            functions (dict): A dictionary of functions retrieved from the source codes.
        """
        pp.pretty_print(f"New listing detected for {self.proposal_address}", pp.Colors.WARNING)
        listings = self.__extract_listings_from_function(
            functions.get("newListings", functions.get("newListingsCustom"))._node
        )
        if listings:
            pp.pretty_print(f"Found {len(listings)} new listings", pp.Colors.SUCCESS)
        else:
            pp.pretty_print(f"Failed to extract listings from function", pp.Colors.FAILURE)

        approval_calls, supply_calls = self.__extract_approval_and_supply_calls(
            functions.get("_postExecute")._node
        )
        approval_calls = {call.asset: call for call in approval_calls}
        supply_calls = {call.asset: call for call in supply_calls}

        for listing in listings:
            self._check_listing_calls(listing, approval_calls, supply_calls)

    def _check_listing_calls(self, listing: ListingDetails, approval_calls: dict, supply_calls: dict) -> None:
        """
        Checks the approval and supply calls for a given listing.
        This method verifies if there are approval and supply calls for the given listing and prints
        messages indicating the status of these calls.
        Args:
            listing (ListingDetails): The details of the listing to check.
            approval_calls (dict): A dictionary of approval calls.
            supply_calls (dict): A dictionary of supply calls.
        """
        pp.pretty_print(f"Listing: {listing}", pp.Colors.WARNING)
        if listing.asset not in approval_calls:
            pp.pretty_print(f"Missing approval call for {listing.asset}", pp.Colors.FAILURE)
            self._write_to_file("missing_approval_calls.json", listing.dict())
        else:
            pp.pretty_print(f"Found approval call for {listing.asset}", pp.Colors.SUCCESS)
            self._write_to_file("found_approval_calls.json", listing.dict())
        if listing.asset not in supply_calls:
            pp.pretty_print(f"Missing supply call for {listing.asset}", pp.Colors.FAILURE)
            self._write_to_file("missing_supply_calls.json", listing.dict())
        else:
            pp.pretty_print(f"Found supply call for {listing.asset}", pp.Colors.SUCCESS)
            self._write_to_file("found_supply_calls.json", listing.dict())

    def __extract_listings_from_function(self, function_node: dict) -> list[ListingDetails]:
        """
        Extracts new listings information from the function node.
        This method simplifies the extraction of new listings by checking the function node for
        variable declarations related to listings and extracting the relevant details.
        Args:
            function_node (dict): The function node to extract listings from.
        Returns:
            list[ListingDetails]: A list of ListingDetails objects representing the new listings.
        """
        if function_node.get('type') != 'FunctionDefinition':
            return []

        new_listings = []
        for statement in function_node.get('body', {}).get('statements', []):
            if statement.get('type') == 'VariableDeclarationStatement':
                for var in statement.get('variables', []):
                    if var.get('typeName', {}).get('baseTypeName', {}).get('namePath') == 'IAaveV3ConfigEngine.Listing':
                        new_listings.extend(self._extract_listings_from_statements(function_node))
        return new_listings

    def _extract_listings_from_statements(self, function_node: dict) -> list[ListingDetails]:
        """
        Extracts listings from the statements in the function node.
        This method iterates over the statements in the function node and extracts listing details
        from the relevant expressions.
        Args:
            function_node (dict): The function node to extract listings from.
        Returns:
            list[ListingDetails]: A list of ListingDetails objects representing the new listings.
        """
        new_listings = []
        for expr_stmt in function_node.get('body', {}).get('statements', []):
            if expr_stmt.get('type') == 'ExpressionStatement':
                expr = expr_stmt.get('expression', {})
                if expr.get('type') == 'BinaryOperation' and expr.get('operator') == '=':
                    left = expr.get('left', {})
                    if left.get('type') == 'IndexAccess' and left.get('base', {}).get('name') == 'listings':
                        listing_details = self.__extract_listing_details(expr.get('right', {}).get('arguments', []))
                        if listing_details:
                            new_listings.append(listing_details)
        return new_listings

    def __extract_listing_details(self, arguments: list[dict]) -> ListingDetails:
        """
        Extracts listing details from function arguments.
        This method extracts the asset, asset symbol, and price feed address from the function arguments
        and returns a ListingDetails object.
        Args:
            arguments (list[Node]): The list of function arguments to extract details from.
        Returns:
            ListingDetails: An object containing the extracted listing details.
        """
        listing_info = {}
        if arguments:
            listing_info['asset'] = arguments[0].get('name')
            listing_info['assetSymbol'] = arguments[1].get('value') if len(arguments) > 1 else None
            listing_info['priceFeedAddress'] = arguments[2].get('number') if len(arguments) > 2 else None
        return ListingDetails(**listing_info)

    def __extract_approval_and_supply_calls(self, function_node: dict) -> tuple[list[FunctionCallDetails], list[FunctionCallDetails]]:
        """
        Extracts approval and supply calls from the function node.
        This method iterates over the statements in the function node and extracts details of approval
        and supply calls.
        Args:
            function_node (Node): The function node to extract calls from.
        Returns:
            tuple[list[FunctionCallDetails], list[FunctionCallDetails]]: Two lists containing the details
            of approval and supply calls respectively.
        """
        approval_calls, supply_calls = [], []
        for statement in function_node.get('body', {}).get('statements', []):
            if statement.get('type') == 'ExpressionStatement':
                expression = statement.get('expression', {})
                if expression.get('type') == 'FunctionCall':
                    function_name = expression.get('expression', {}).get('name', "")
                    if "approve" in function_name or "forceApprove" in function_name:
                        approval_calls.append(self._extract_function_call_details(expression))
                    elif 'supply' in function_name:
                        supply_calls.append(self._extract_function_call_details(expression))
        return approval_calls, supply_calls

    def _extract_function_call_details(self, expression: dict) -> FunctionCallDetails:
        """
        Extracts details of a function call.
        This method extracts the pool, asset, and asset seed from the function call expression
        and returns a FunctionCallDetails object.
        Args:
            expression (dict): The function call expression to extract details from.
        Returns:
            FunctionCallDetails: An object containing the extracted function call details.
        """
        pool = expression['arguments'][0]['expression']['name']
        asset = expression['arguments'][1]['name']
        asset_seed = expression['arguments'][2]['name']
        return FunctionCallDetails(pool=pool, asset=asset, asset_seed=asset_seed)
