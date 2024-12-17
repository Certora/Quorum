from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from Quorum.llm.chains.cached_llm import CachedLLM
from Quorum.llm.jinja_utils import render_prompt


class ListingDetails(BaseModel):
    """
    A model representing details for listing an asset.

    This class extends BaseModel and contains information necessary for listing
    operations including asset details, supply amount, and operation indicators.

    Attributes:
        asset (str): The identifier or symbol of the asset to be listed.
        supply_seed_amount (Optional[float]): The initial amount to seed the supply with.
            Defaults to None if not specified.
        supply_indicator (bool): Flag indicating whether a supply operation is being
            performed for the asset. True if supply is called, False otherwise.
        approve_indicator (bool): Flag indicating whether an approval operation is
            being performed for the asset.
    """
    asset_symbol: str = Field(description="The asset symbol to be listed.")
    asset_address: str = Field(description="The asset address to be listed.")
    supply_seed_amount: Optional[float] = Field(description="The amount of supply seed.")
    supply_indicator: bool = Field(
        description="The indicator for supply being call for the asset. True if supply is being called. False otherwise."
    )
    approve_indicator: bool = Field(
        description="The indicator for approval being call for the asset."
    )

class ListingArray(BaseModel):
    """
    A container class for holding multiple listing details in a structured format.

    This class represents an array of `ListingDetails` objects, each containing specific
    parameters and configurations for asset listings. It is designed to handle multiple
    listings within a single proposal.

    Attributes:
        listings (list[ListingDetails]): A list containing individual listing details
            for each asset proposed to be listed. Each element in the list is a
            ListingDetails object specifying the complete configuration for that
            particular asset listing.
    """
    listings: list[ListingDetails] = Field(description="The list of assets to be listed.")

class FirstDepositChain(CachedLLM):

    def __init__(self):
        super().__init__()
        structured_llm = self.llm.with_structured_output(ListingArray)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant. Answer all questions to the best of your ability."),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        self.app = prompt | structured_llm

    
    def execute(
            self,
            source_code: str,
            prompt_template: str = "first_deposit_prompt.j2"
    ) -> ListingArray | None:
        """
        Executes the first deposit chain workflow by rendering prompts, interacting with the LLM,
        and retrieving the final listing details.

        The first deposit chain workflow consists of:
        - Rendering the prompt with the provided source code data.
        - Invoking the LLM with the rendered prompt.

        Args:
            source_code (str): The Solidity source code to be validated.
            prompt_template (str): The Jinja template for prompting the LLM.

        Returns:
            ListingArray: The final listing details from the LLM or None if the LLM fails to execute.
        """
        prompt_rendered = render_prompt(
            prompt_template,
            {"source_code": source_code}
        )
        return self.app.invoke(
            {"messages": [prompt_rendered]}
        )
        