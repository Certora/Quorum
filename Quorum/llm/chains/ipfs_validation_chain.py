from typing import Optional
from pydantic import BaseModel, Field

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

from Quorum.llm.jinja_utils import render_prompt
from Quorum.llm.chains.cached_llm import CachedLLM

class Incompatibility(BaseModel):
    """
    Incompatibility is a Pydantic model that represents a mismatch between the IPFS and Solidity payloads.
    """
    subject: str = Field(..., description="The subject of the incompatibility (e.g. disagreement between IPFS and Solidity).")
    subject_in_ipfs: str = Field(..., description="The subject details as described in the IPFS payload.")
    subject_in_solidity: str = Field(..., description="The subject details as described in the Solidity payload.")
    description: str = Field(..., description="A detailed description of the incompatibility.")

class IncompatibilityArray(BaseModel):
    """
    IncompatibilityArray is a Pydantic model that represents a list of incompatibilities between the IPFS and Solidity payloads.
    """
    incompatibilities: Optional[list[Incompatibility]] = Field(
        default=None,
        description="A list of incompatibilities between the IPFS and Solidity payloads."
    )

class IPFSValidationChain(CachedLLM):
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
        super().__init__()

        self.structured_llm = self.llm.with_structured_output(IncompatibilityArray)
        
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

    def execute(self, prompt_templates: list[str], ipfs: str, payload: str, thread_id: int = 1) -> IncompatibilityArray:
        """
        Executes the IPFS validation workflow by rendering prompts, interacting with the LLM,
        and retrieving the final validation report.

        The validation workflow consists of:
        For each prompt template:
            - Render the prompt with the provided IPFS and payload data.
            - Invoke the LLM with the rendered prompt.

        Args:
            prompt_templates (list[str]): A list of Jinja templates for prompting the LLM.
            ipf (str): The IPFS content associated with the proposal.
            payload (str): The Solidity payload code to be validated against the IPFS content.
            thread_id (int): The thread ID to associate with the LLM interaction

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
                config={"configurable": {"thread_id": f"{thread_id}"}},
            )

        return self.structured_llm.invoke([h.content for h in history["messages"]])
