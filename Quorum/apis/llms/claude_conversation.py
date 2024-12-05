from Quorum.apis.llms.llm_conversation import LLMConversation

from anthropic import Anthropic


HAIKU = 'claude-3-5-haiku-20241022'


class ClaudeConversation(LLMConversation):
    def __init__(self, api_key: str, model: str = HAIKU):
        '''
        Summary
        -------
        Initialize a conversation manager for Claude.
        
        Parameters
        ----------
        api_key : str
            Your Anthropic API key
        model : str, default = 'claude-3-5-haiku-20241022'
            The Claude model to use
        '''
        super().__init__()
        self.client = Anthropic(api_key=api_key)
        self.model = model
