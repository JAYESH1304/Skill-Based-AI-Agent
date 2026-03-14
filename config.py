"""Configuration management for the agent system."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for agent settings."""
    
    # Azure OpenAI Settings
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    # Azure AD Authentication (optional)
    AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
    AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
    AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
    
    # Agent Settings
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4000"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
    
    # Skills Directory
    BASE_DIR = Path(__file__).parent
    SKILLS_DIRECTORY = Path(os.getenv("SKILLS_DIRECTORY", BASE_DIR / "skills"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        required = [
            ("AZURE_OPENAI_ENDPOINT", cls.AZURE_OPENAI_ENDPOINT),
            ("AZURE_OPENAI_DEPLOYMENT_NAME", cls.AZURE_OPENAI_DEPLOYMENT_NAME),
        ]
        
        # Either API key or Azure AD credentials required
        has_api_key = bool(cls.AZURE_OPENAI_API_KEY)
        has_azure_ad = all([cls.AZURE_TENANT_ID, cls.AZURE_CLIENT_ID, cls.AZURE_CLIENT_SECRET])
        
        if not has_api_key and not has_azure_ad:
            raise ValueError(
                "Either AZURE_OPENAI_API_KEY or Azure AD credentials "
                "(AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET) must be provided"
            )
        
        for name, value in required:
            if not value:
                raise ValueError(f"Missing required configuration: {name}")
        
        return True

# Validate configuration on import
Config.validate()