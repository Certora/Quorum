import quorum.utils.pretty_printer as pp
from quorum.apis.block_explorers.source_code import SourceCode
from quorum.checks.diff import DiffCheck
from quorum.utils.chain_enum import Chain


class ReviewDiffCheck(DiffCheck):
    def __init__(
        self,
        customer: str,
        chain: Chain,
        proposal_address: str,
        source_codes: list[SourceCode],
    ):
        super().__init__(customer, chain, proposal_address, source_codes)
        self.target_repo = self.customer_folder / "review_module"

    def find_diffs(self) -> list[SourceCode]:
        pp.pprint(f"Review repo cloned under: {self.target_repo}", pp.Colors.INFO)
        return super().find_diffs()
