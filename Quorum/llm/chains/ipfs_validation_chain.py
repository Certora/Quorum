from Quorum.llm.jinja_utils import render_prompt
from Quorum.config import ANTHROPIC_MODEL

from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.globals import set_llm_cache
from langchain_core.output_parsers import StrOutputParser
from langchain_anthropic import ChatAnthropic
from langchain_ollama.chat_models import ChatOllama
from langchain_community.cache import SQLiteCache


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

        #Initialize the Anthropic LLM with the specified model and configurations
        self.llm = ChatAnthropic(
            model=ANTHROPIC_MODEL,
            cache=True,
            max_retries=3,
        )

        # For testing purposes, we will use the ChatOllama model instead of ChatAnthropic
        # self.llm = ChatOllama(
        #     model="llama3.2",
        #     cache=True,
        #     max_retries=3,
        #     temperature=0.0,
        # )

        # Define the workflow for the IPFS validation chain
        workflow = StateGraph(state_schema=MessagesState)
        workflow.add_node("model", self.__call_model)
        workflow.add_edge(START, "model")
        memory = MemorySaver()

        self.app = workflow.compile(checkpointer=memory)

    # Define the function that calls the model
    def __call_model(self, state: MessagesState) -> MessagesState:
        system_prompt = (
            "You are a helpful assistant. "
            "Answer all questions to the best of your ability."
        )
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = self.llm.invoke(messages)
        return {"messages": response}

    def execute(self, prompt_templates: list[str], ipfs: str, payload: str) -> str:
        """
        Executes the IPFS validation workflow by rendering prompts, interacting with the LLM,
        and retrieving the final validation report.

        The validation workflow consists of:
        For each prompt template:
            - Render the prompt with the provided IPFS and payload data.
            - Invoke the LLM with the rendered prompt.

        Args:
            prompt_templates (tuple[str, str]): A tuple containing the filenames of the Jinja2
                templates for the first and second prompts, respectively.
            ipf (str): The IPFS content associated with the proposal.
            payload (str): The Solidity payload code to be validated against the IPFS content.

        Returns:
            str: The final response from the LLM, detailing the validation results.
        """
        for template in prompt_templates:

            prompt_rendered = render_prompt(
                template,
                {"ipfs": ipfs, "payload": payload}
            )

            history = self.app.invoke(
                {"messages": [HumanMessage(prompt_rendered)]},
                config={"configurable": {"thread_id": "1"}},
            )

        return StrOutputParser().parse(history["messages"][-1].content)
