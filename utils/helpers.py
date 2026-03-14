"""Helper utilities for the agent system."""

import tiktoken
from typing import List, Dict, Any

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count tokens in a text string.
    
    Args:
        text: Text to count tokens for
        model: Model name for encoding
        
    Returns:
        Number of tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    return len(encoding.encode(text))

def truncate_text(text: str, max_tokens: int, model: str = "gpt-4") -> str:
    """
    Truncate text to fit within token limit.
    
    Args:
        text: Text to truncate
        max_tokens: Maximum number of tokens
        model: Model name for encoding
        
    Returns:
        Truncated text
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    tokens = encoding.encode(text)
    if len(tokens) <= max_tokens:
        return text
    
    truncated_tokens = tokens[:max_tokens]
    return encoding.decode(truncated_tokens)

def format_chat_history(messages: List[Dict[str, str]], max_messages: int = 10) -> str:
    """
    Format chat history for display.
    
    Args:
        messages: List of message dictionaries
        max_messages: Maximum number of messages to include
        
    Returns:
        Formatted chat history string
    """
    recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages
    
    formatted = []
    for msg in recent_messages:
        role = msg.get("role", "unknown").capitalize()
        content = msg.get("content", "")
        formatted.append(f"{role}: {content}")
    
    return "\n\n".join(formatted)

def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """
    Extract code blocks from markdown text.
    
    Args:
        text: Markdown text containing code blocks
        
    Returns:
        List of dictionaries with 'language' and 'code' keys
    """
    import re
    
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    code_blocks = []
    for language, code in matches:
        code_blocks.append({
            'language': language or 'text',
            'code': code.strip()
        })
    
    return code_blocks