"""Azure OpenAI client wrapper."""

from typing import List, Dict, Any, Optional
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from config import Config
from utils.logger import logger

class AzureOpenAIClient:
    """Wrapper for Azure OpenAI API client."""
    
    def __init__(self):
        """Initialize the Azure OpenAI client."""
        self.endpoint = Config.AZURE_OPENAI_ENDPOINT
        self.deployment = Config.AZURE_OPENAI_DEPLOYMENT_NAME
        self.api_version = Config.AZURE_OPENAI_API_VERSION
        
        # Initialize client based on authentication method
        if Config.AZURE_OPENAI_API_KEY:
            logger.info("Using API key authentication")
            self.client = AzureOpenAI(
                api_key=Config.AZURE_OPENAI_API_KEY,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
        else:
            logger.info("Using Azure AD authentication")
            credential = DefaultAzureCredential()
            token_provider = get_bearer_token_provider(
                credential,
                "https://cognitiveservices.azure.com/.default"
            )
            self.client = AzureOpenAI(
                azure_ad_token_provider=token_provider,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
        
        logger.info(f"Azure OpenAI client initialized with deployment: {self.deployment}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Any:
        """
        Generate a chat completion.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Completion response or stream iterator
        """
        temp = temperature if temperature is not None else Config.TEMPERATURE
        tokens = max_tokens if max_tokens is not None else Config.MAX_TOKENS
        
        try:
            logger.debug(f"Sending chat completion request with {len(messages)} messages")
            
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                temperature=temp,
                max_tokens=tokens,
                stream=stream
            )
            
            if not stream:
                logger.debug(f"Received completion response: {response.choices[0].message.content[:100]}...")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in chat completion: {str(e)}")
            raise
    
    def get_response_text(self, response: Any) -> str:
        """
        Extract text from a completion response.
        
        Args:
            response: Completion response object
            
        Returns:
            Response text content
        """
        try:
            return response.choices[0].message.content
        except (AttributeError, IndexError) as e:
            logger.error(f"Error extracting response text: {str(e)}")
            return ""
    
    def stream_response(self, stream):
        """
        Generator to yield text chunks from a streaming response.
        
        Args:
            stream: Stream iterator from chat_completion
            
        Yields:
            Text chunks from the stream
        """
        try:
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Error in stream response: {str(e)}")
            yield f"\n\n[Error: {str(e)}]"