from pathlib import Path
import re
from dataclasses import dataclass

from Quorum.apis.price_feeds import PriceFeedProviderBase, PriceFeedData
from Quorum.utils.chain_enum import Chain
from Quorum.checks.check import Check
from Quorum.apis.block_explorers.source_code import SourceCode
import Quorum.utils.pretty_printer as pp


class PriceFeedCheck(Check):
    """
    The PriceFeedCheck class is responsible for verifying the price feed addresses in the source code
    against official Chainlink or Chronical data.
    """
    def __init__(
            self,
            customer: str,
            chain: Chain,
            proposal_address: str,
            source_codes: list[SourceCode],
            price_feed_providers: list[PriceFeedProviderBase],
            token_providers: list[PriceFeedProviderBase]
    ) -> None:
        """
        Initializes the PriceFeedCheck object with customer information, proposal address, 
        and source codes to be checked.

        Args:
            customer (str): The name of the customer for whom the verification is being performed.
            chain (Chain): The blockchain network to verify the price feeds against.
            proposal_address (str): The address of the proposal being verified.
            source_codes (list[SourceCode]): A list of source code objects containing the Solidity contracts to be checked.
            providers (list[PriceFeedProviderInterface]): A list of price feed providers to be used for verification.
        """
        super().__init__(customer, chain, proposal_address, source_codes)
        self.address_pattern = r'0x[a-fA-F0-9]{40}'
        self.price_feed_providers = price_feed_providers
        self.token_providers = token_providers

    @dataclass
    class PriceFeedResult:
        '''
        This dataclass helps organize the results of the check for printing them to the user.
        '''
        address: str
        found_on: str
        price_feed: PriceFeedData

        def __hash__(self):
            return hash(self.address)

    def __check_address(self, address: str, providers: list[PriceFeedProviderBase]) -> PriceFeedResult | None:
        """
        Check if the given address is present in the price feed providers.

        Args:
            address (str): The address to be checked.
            providers (list[PriceFeedProviderBase]): The list of price feed providers to check against.

        Returns:
            PriceFeedResult | None: The price feed data if the address is found, otherwise None.
        """
        for provider in providers:
            if (price_feed := provider.get_price_feed(self.chain, address)):
                return PriceFeedCheck.PriceFeedResult(address, provider.get_name(), price_feed)
        return None

    def verify_price_feed(self) -> None:
        """
        Verifies the price feed addresses in the source code against official Chainlink or Chronicle data.

        This method iterates through each source code file to find and verify the address variables
        against the official Chainlink and Chronicle price feeds. It categorizes the addresses into
        verified and violated based on whether they are found in the official source.
        """
        verified_price_feeds: set[PriceFeedCheck.PriceFeedResult] = set()
        verified_tokens: set[PriceFeedCheck.PriceFeedResult] = set()
        unverified_addresses: set[str] = set()

        # Iterate through each source code file to find and verify address variables
        for source_code in self.source_codes:
            verified_sources_path = f"{Path(source_code.file_name).stem.removesuffix('.sol')}/verified_sources.json"
            verified_variables = []

            # Combine all lines into a single string
            contract_text = '\n'.join(source_code.file_content)
            
            # Remove comments from the source code
            clean_text = PriceFeedCheck.remove_solidity_comments(contract_text)
            
            # Extract unique addresses using regex
            addresses = set(re.findall(self.address_pattern, clean_text))

            for address in addresses:
                if res := self.__check_address(address, self.price_feed_providers):
                    verified_variables.append(res.price_feed.model_dump())
                    verified_price_feeds.add(res)
                elif res := self.__check_address(address, self.token_providers):
                    verified_variables.append(res.price_feed.model_dump())
                    verified_tokens.add(res)
                else:
                    unverified_addresses.add(address)

            if verified_variables:
                self._write_to_file(verified_sources_path, verified_variables)
        
        num_addresses = len(verified_price_feeds) + len(verified_tokens) + len(unverified_addresses)
        pp.pprint(f'{num_addresses} addresses identified in the payload.\n', pp.Colors.INFO)

        # Print price feed validation
        pp.pprint('Price Feed Validation', pp.Colors.INFO, pp.Heading.HEADING_3)
        msg = (f'{len(verified_price_feeds)}/{num_addresses} '
                                     'were identified as price feeds of the configured providers:\n')
        for i, var_res in enumerate(verified_price_feeds, 1):
            msg += (f'\t{i}. {var_res.address} found on {var_res.found_on}\n'
                    f'\t   Name: {var_res.price_feed.name}\n'
                    f'\t   Decimals: {var_res.price_feed.decimals}\n')
        pp.pprint(msg, pp.Colors.SUCCESS)

        # Print token validation
        pp.pprint('Token Validation', pp.Colors.INFO, pp.Heading.HEADING_3)
        msg = (f'{len(verified_tokens)}/{num_addresses} '
                                'were identified as tokens of the configured providers:\n')
        for i, var_res in enumerate(verified_tokens, 1):
            msg += (f'\t{i}. {var_res.address} found on {var_res.found_on}\n'
                    f'\t   Name: {var_res.price_feed.name}\n'
                    f'\t   Symbol: {var_res.price_feed.pair}\n'
                    f'\t   Decimals: {var_res.price_feed.decimals}\n')
        pp.pprint(msg, pp.Colors.SUCCESS)

        # Print not found
        msg = (f'{len(unverified_addresses)}/{num_addresses} '
               'explicit addresses were not identified using any provider:\n')
        for i, address in enumerate(unverified_addresses, 1):
            msg += f'\t{i}. {address}\n'
        pp.pprint(msg, pp.Colors.FAILURE)

    @staticmethod    
    def remove_solidity_comments(source_code: str) -> str:
        """
        Removes single-line and multi-line comments from Solidity source code.
        
        Args:
            source_code (str): The Solidity source code as a single string.
        
        Returns:
            str: The source code with comments removed.
        """
        # Regex pattern to match single-line comments (//...)
        single_line_comment_pattern = r'//.*?$'
        
        # Regex pattern to match multi-line comments (/*...*/)
        multi_line_comment_pattern = r'/\*.*?\*/'
        
        # First, remove multi-line comments
        source_code = re.sub(multi_line_comment_pattern, '', source_code, flags=re.DOTALL)
        
        # Then, remove single-line comments
        source_code = re.sub(single_line_comment_pattern, '', source_code, flags=re.MULTILINE)
        
        return source_code
