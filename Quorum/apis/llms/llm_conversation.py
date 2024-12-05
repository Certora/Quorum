from enum import StrEnum, auto


class MessageRole(StrEnum):
    USER = auto()
    ASSISTANT = auto()


MAX_TOKENS = 1024


class LLMConversation:
    '''
    Description
    -----------
    At least GPT and Claude share the exact same API. Probably other LLMs use the same API as well,
    just using different clients. This abstract class builds is expected to be inherited and build
    the relevant client to be used with the same implementation of interacting with the LLM while 
    maintaining a conversation context.
    '''
    def __init__(self):
        '''
        Summary
        -------
        Initialize a conversation manager for an LLM.
        '''
        self.client = None
        self.model = None
        self.messages: list[dict[str, str]] = []
        
    def add_message(self, role: str, content: str) -> None:
        '''
        Summary
        -------
        Add a message to the conversation history.
        
        Parameters
        ----------
        role : MessageRole
            What role to use.
        content : str
            The message content.
        '''
        self.messages.append({
            'role': str(role),
            'content': content
        })
    
    def send_message(self, message: str) -> str:
        '''
        Summary
        -------
        Send a message to the LLM and get the response, maintaining conversation history.
        
        Parameters
        ----------
        message : str
            The message to send.
            
        Returns
        -------
        str
            The response.
        '''
        # Add user message to history
        self.add_message(MessageRole.USER, message)
        
        # Get response from LLM
        response = self.client.messages.create(
            max_tokens=MAX_TOKENS,
            model=self.model,
            messages=self.messages
        )
        
        # Add LLM's response to history
        # `response.content` is a list of responses. The LLM can generate more than 1 answer (configurable).
        assistant_message = response.content[0].text
        self.add_message(MessageRole.ASSISTANT, assistant_message)
        
        return assistant_message
    
    def view_history(self) -> None:
        '''
        Summary
        -------
        Print the entire conversation history.
        '''
        for msg in self.messages:
            role = msg['role'].upper()
            content = msg['content']
            print(f"\n{role}: {content}")
