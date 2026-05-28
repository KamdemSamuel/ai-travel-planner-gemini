"""
Configuration Management for AI Travel Planner
Handles environment variables, API keys, and LLM provider settings
"""

import os
from enum import Enum
from typing import Optional
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    GOOGLE = "google"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"


class ProviderModel(str, Enum):
    """Model selections for each provider"""
    # Google Gemini models
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    
    # OpenAI models
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4 = "gpt-4"
    GPT_35_TURBO = "gpt-3.5-turbo"
    
    # Anthropic models
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    
    # OpenRouter meta-models
    OPENROUTER_AUTO = "auto"  # Automatically selects best model
    OPENROUTER_CLAUDE_3_SONNET = "anthropic/claude-3-sonnet"
    OPENROUTER_GPT_4 = "openai/gpt-4-turbo"


@dataclass
class APIConfig:
    """Configuration for each LLM provider"""
    
    # Google Gemini
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GOOGLE_MODEL: ProviderModel = ProviderModel.GEMINI_2_0_FLASH
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: ProviderModel = ProviderModel.GPT_4_TURBO
    OPENAI_ORG_ID: Optional[str] = os.getenv("OPENAI_ORG_ID")
    
    # Anthropic
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: ProviderModel = ProviderModel.CLAUDE_3_SONNET
    
    # OpenRouter
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL: ProviderModel = ProviderModel.OPENROUTER_AUTO
    
    # Default provider
    DEFAULT_PROVIDER: LLMProvider = LLMProvider(
        os.getenv("DEFAULT_LLM_PROVIDER", "google").lower()
    )
    
    # General settings
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
    
    def __post_init__(self):
        """Validate that at least one API key is configured"""
        available_providers = self.get_available_providers()
        if not available_providers:
            raise ValueError(
                "No LLM API keys found in .env file. "
                "Please configure at least one provider: "
                "GOOGLE_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, or OPENROUTER_API_KEY"
            )
    
    def get_available_providers(self) -> list[LLMProvider]:
        """Get list of configured providers"""
        providers = []
        
        if self.GOOGLE_API_KEY:
            providers.append(LLMProvider.GOOGLE)
        if self.OPENAI_API_KEY:
            providers.append(LLMProvider.OPENAI)
        if self.ANTHROPIC_API_KEY:
            providers.append(LLMProvider.ANTHROPIC)
        if self.OPENROUTER_API_KEY:
            providers.append(LLMProvider.OPENROUTER)
        
        return providers
    
    def is_provider_available(self, provider: LLMProvider) -> bool:
        """Check if a specific provider is available"""
        return provider in self.get_available_providers()
    
    def get_api_key(self, provider: LLMProvider) -> Optional[str]:
        """Get API key for specified provider"""
        api_keys = {
            LLMProvider.GOOGLE: self.GOOGLE_API_KEY,
            LLMProvider.OPENAI: self.OPENAI_API_KEY,
            LLMProvider.ANTHROPIC: self.ANTHROPIC_API_KEY,
            LLMProvider.OPENROUTER: self.OPENROUTER_API_KEY,
        }
        return api_keys.get(provider)
    
    def get_model(self, provider: LLMProvider) -> str:
        """Get model name for specified provider"""
        models = {
            LLMProvider.GOOGLE: self.GOOGLE_MODEL.value,
            LLMProvider.OPENAI: self.OPENAI_MODEL.value,
            LLMProvider.ANTHROPIC: self.ANTHROPIC_MODEL.value,
            LLMProvider.OPENROUTER: self.OPENROUTER_MODEL.value,
        }
        return models.get(provider, "")


# Global config instance
config = APIConfig()


# Fallback provider order
PROVIDER_FALLBACK_ORDER = [
    LLMProvider.GOOGLE,
    LLMProvider.OPENAI,
    LLMProvider.ANTHROPIC,
    LLMProvider.OPENROUTER,
]


def get_available_provider(
    preferred: Optional[LLMProvider] = None
) -> LLMProvider:
    """
    Get an available provider, respecting preference and fallback order
    
    Args:
        preferred: Preferred provider, will use if available
    
    Returns:
        Available LLMProvider
    
    Raises:
        ValueError: If no providers are available
    """
    if preferred and config.is_provider_available(preferred):
        return preferred
    
    for provider in PROVIDER_FALLBACK_ORDER:
        if config.is_provider_available(provider):
            return provider
    
    raise ValueError("No LLM providers are available")


# Temperature presets for different use cases
TEMPERATURE_PRESETS = {
    "creative": 0.9,        # For travel inspirations
    "balanced": 0.7,        # Default for travel planning
    "precise": 0.3,         # For cost calculations
    "deterministic": 0.0,   # For testing
}


# Prompt templates configuration
PROMPT_CONFIG = {
    "max_tokens": {
        "short": 500,
        "medium": 1500,
        "long": 3000,
    },
    "language": os.getenv("LANGUAGE", "en"),  # Support multilingual prompts
}


if __name__ == "__main__":
    # Debug: Show available providers
    print("🔧 Configuration Check:")
    print(f"  Available providers: {config.get_available_providers()}")
    print(f"  Default provider: {config.DEFAULT_PROVIDER}")
    print(f"  Enable caching: {config.ENABLE_CACHING}")
    print(f"  Max retries: {config.MAX_RETRIES}")
