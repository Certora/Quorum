from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.globals import set_llm_cache
from langchain_core.output_parsers import StrOutputParser
from langchain_anthropic import ChatAnthropic
from langchain_ollama.chat_models import ChatOllama
from langchain_community.cache import SQLiteCache


from Quorum.llm.jinja_utils import render_prompt


class IPFSValidationChain:
    """
    IPFSValidationChain is responsible for validating the integrity and accuracy of an IPFS payload
    by comparing it against an actual Solidity payload. It leverages LangChain's capabilities to
    orchestrate a sequential interaction with the Anthropic LLM, ensuring that the validation process
    is both efficient and contextually aware.

    Attributes:
        chain (SequentialChain): A LangChain SequentialChain that manages the sequence of LLM interactions.
    """

    def __init__(self):
        """
        Initializes the IPFSValidationChain by setting up the LLM, caching mechanism, and the sequential
        chain of prompts. It configures the Anthropic LLM with specified parameters and prepares the
        prompt templates for execution.
        """
        # Configure caching to optimize LLM interactions and reduce redundant computations
        set_llm_cache(
            SQLiteCache(
                database_path=f"{Path(__file__).parent.parent / 'cache' / f'{Path(__file__).stem}_cache.db'}"
            )
        )

        # Initialize the Anthropic LLM with the specified model and configurations
        # self.llm = ChatAnthropic(
        #     model="claude-3-5-sonnet-20240620",
        #     cache=True,
        #     max_retries=3,
        # )

        # For testing purposes, we will use the ChatOllama model instead of ChatAnthropic
        self.llm = ChatOllama(
            model="llama3.2",
            cache=False,
            max_retries=3,
            temperature=0.0,
        )

        # Define the prompt template using system and placeholder messages
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="You are a helpful assistant. Answer all questions to the best of your ability."
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        # Combine the prompt template with the LLM to form the sequential chain
        self.chain = prompt | self.llm | StrOutputParser()

    def execute(self, prompt_templates: tuple[str, str], ipfs: str, payload: str) -> str:
        """
        Executes the IPFS validation workflow by rendering prompts, interacting with the LLM,
        and retrieving the final validation report.

        The validation workflow consists of:
            1. Rendering the first prompt with the provided IPFS and Solidity payloads.
            2. Rendering the second prompt that contains the guide lines for the answer.
            3. Sending both prompts to the LLM in a sequential manner.
            4. Returning the final response from the LLM, which contains the validation findings.

        Args:
            prompt_templates (tuple[str, str]): A tuple containing the filenames of the Jinja2
                templates for the first and second prompts, respectively.
            ipf (str): The IPFS content associated with the proposal.
            payload (str): The Solidity payload code to be validated against the IPFS content.

        Returns:
            str: The final response from the LLM, detailing the validation results.

        Raises:
            ValueError: If the number of prompt templates provided is not exactly two.
            Exception: Propagates any exceptions encountered during the chain execution.
        """
        # Render the first prompt with IPFS and payload context
        prompt1_rendered = render_prompt(
            prompt_templates[0],
            {"ipfs": ipfs, "payload": payload}
        )

        # Render the second prompt, potentially utilizing conversation history
        prompt2_rendered = render_prompt(
            prompt_templates[1],
            {}
        )

        # Create a list of HumanMessage instances for the prompts
        messages = [
            HumanMessage(content=prompt1_rendered),
            HumanMessage(content=prompt2_rendered),
        ]

        # Invoke the sequential chain with the prepared messages
        response = self.chain.invoke(
            {
                "messages": messages,
            }
        )

        return response
