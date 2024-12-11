from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_anthropic import ChatAnthropic
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache

from Quorum.llm.jinja_utils import render_prompt

set_llm_cache(SQLiteCache(database_path=f"{Path(__file__).parent.parent / 'cache' / f'{Path(__file__).stem}cache.db'}"))

class IPFSValidationChain:
    """
    This chain is responsible for validating the IPFS payload by comparing it with the actual payload.
    """
    
    def __init__(self):
        model = ChatAnthropic(
            model="claude-3-5-sonnet-20240620",
            cache=True,
            max_retries=3,
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="You are a helpful assistant. Answer all questions to the best of your ability."
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        self.chain = prompt | model

    def execute(self, prompt_templates: list[str], ipf: str, payload: str) -> str:
        """
        Executes the IPFS validation chain.

        Args:
            prompt_templates (list[str]): The list of Jinja templates for the prompts.
            ipf (str): The IPFS payload.
            payload (str): The actual payload.

        Returns:
            str: The response from the LLM.
        """
        messages = [
            HumanMessage(content=render_prompt(prompt_templates[0], {"ipfs": ipf, "payload": payload})),
            HumanMessage(content=render_prompt(prompt_templates[1], {})),
        ]
        return self.chain.invoke(
            {
                "messages": messages,
            }
        )
