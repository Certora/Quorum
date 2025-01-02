from pathlib import Path
import re
from dataclasses import dataclass

from Quorum.apis.price_feeds import PriceFeedProviderBase, CoinGeckoAPI
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
            providers: list[PriceFeedProviderBase]
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
        self.providers = providers

    @dataclass
    class PriceFeedResult:
        '''
        This dataclass helps organize the results of the check for printing them to the user.
        '''
        address: str
        found_on: str
        price_feed: dict

        def __hash__(self):
            return hash(self.address)

    def __check_price_feed_address(self, address: str) -> PriceFeedResult | None:
        """
        Check if the given address is present in the price feed providers.

        Args:
            address (str): The address to be checked.

        Returns:
            PriceFeedResult | None: The price feed data if the address is found, otherwise None.
        """
        for provider in self.providers:
            if (price_feed := provider.get_price_feed(self.chain, address)):
                return PriceFeedCheck.PriceFeedResult(address, provider.get_name(), price_feed.model_dump())
        return None

    def verify_price_feed(self) -> None:
        """
        Verifies the price feed addresses in the source code against official Chainlink or Chronicle data.

        This method iterates through each source code file to find and verify the address variables
        against the official Chainlink and Chronicle price feeds. It categorizes the addresses into
        verified and violated based on whether they are found in the official source.
        """
        all_addresses = set()
        overall_verified_vars: set[PriceFeedCheck.PriceFeedResult] = set()
        overall_unverified_vars: set[str] = set()

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
            all_addresses.update(addresses)

            for address in addresses:
                if res := self.__check_price_feed_address(address):
                    verified_variables.append(res.price_feed)
                    overall_verified_vars.add(res)
                else:
                    overall_unverified_vars.add(address)

            if verified_variables:
                self._write_to_file(verified_sources_path, verified_variables)
        
        num_addresses = len(all_addresses)
        pp.pprint(f'{num_addresses} addresses identified in the payload.', pp.Colors.INFO)

        coingecko_name = CoinGeckoAPI().get_name()
        token_validation_res = {r for r in overall_verified_vars if r.found_on == coingecko_name}
        price_feed_validation_res = overall_verified_vars - token_validation_res

        # Print price feed validation
        pp.pprint('Price feed validation', pp.Colors.INFO)
        msg = (f'{len(price_feed_validation_res)}/{num_addresses} '
                                     'were identified as price feeds of the configured providers:\n')
        for i, var_res in enumerate(price_feed_validation_res, 1):
            msg += (f'\t{i}. {var_res.address} found on {var_res.found_on}\n'
                    f"\t   Name: {var_res.price_feed['name']}\n"
                    f"\t   Decimals: {var_res.price_feed['decimals']}\n")
        pp.pprint(msg, pp.Colors.SUCCESS)

        # Print token validation
        pp.pprint('Token validation', pp.Colors.INFO)
        msg = (f'{len(token_validation_res)}/{num_addresses} '
                                'were identified as tokens of the configured providers:\n')
        for i, var_res in enumerate(token_validation_res, 1):
            msg += (f'\t{i}. {var_res.address} found on {var_res.found_on}\n'
                    f"\t   Name: {var_res.price_feed['name']}\n"
                    f"\t   Symbol: {var_res.price_feed['pair']}\n"
                    f"\t   Decimals: {var_res.price_feed['decimals']}\n")
        pp.pprint(msg, pp.Colors.SUCCESS)

        # Print not found
        msg = (f'{len(overall_unverified_vars)}/{num_addresses} '
               'explicit addresses were not identified using any provider:\n')
        for i, address in enumerate(overall_unverified_vars, 1):
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
