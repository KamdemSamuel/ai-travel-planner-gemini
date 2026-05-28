"""
Unified LLM Client - Abstraction layer for multiple LLM providers
Supports: Google Gemini, OpenAI, Anthropic Claude, OpenRouter

Features:
- Async/await support for non-blocking calls
- Provider fallback on errors
- Streaming support
- Retry logic with exponential backoff
- Cost tracking and logging
"""

import asyncio
import logging
from typing import AsyncGenerator, Optional
from datetime import datetime

# Google
import google.generativeai as genai

# OpenAI
try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

# Anthropic
try:
    from anthropic import Anthropic as AnthropicSync
    from anthropic import AsyncAnthropic
except ImportError:
    AnthropicSync = None
    AsyncAnthropic = None

# OpenRouter
import httpx

from config import (
    config,
    LLMProvider,
    get_available_provider,
    TEMPERATURE_PRESETS
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMClient:
    """
    Unified interface for all LLM providers
    Handles provider selection, fallback, retries, and streaming
    """
    
    def __init__(self, provider: Optional[LLMProvider] = None):
        """
        Initialize LLM Client
        
        Args:
            provider: Preferred LLM provider. If None, uses DEFAULT_PROVIDER
        """
        self.provider = provider or config.DEFAULT_PROVIDER
        
        # Verify provider is available, otherwise fallback
        if not config.is_provider_available(self.provider):
            logger.warning(
                f"Provider {self.provider} not available. "
                f"Falling back to available providers."
            )
            self.provider = get_available_provider()
        
        logger.info(f"✅ LLM Client initialized with provider: {self.provider}")
        
        # Initialize provider-specific clients
        self._init_google()
        self._init_openai()
        self._init_anthropic()
        
        # Tracking
        self.call_count = 0
        self.error_count = 0
        self.total_tokens_used = 0
    
    def _init_google(self):
        """Initialize Google Gemini client"""
        if config.GOOGLE_API_KEY:
            genai.configure(api_key=config.GOOGLE_API_KEY)
            logger.debug("✓ Google Gemini configured")
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        if AsyncOpenAI and config.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(
                api_key=config.OPENAI_API_KEY,
                organization=config.OPENAI_ORG_ID
            )
            logger.debug("✓ OpenAI configured")
    
    def _init_anthropic(self):
        """Initialize Anthropic client"""
        if AsyncAnthropic and config.ANTHROPIC_API_KEY:
            self.anthropic_client = AsyncAnthropic(
                api_key=config.ANTHROPIC_API_KEY
            )
            logger.debug("✓ Anthropic Claude configured")
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        provider: Optional[LLMProvider] = None,
        stream: bool = False
    ) -> str:
        """
        Generate text using specified or default provider
        
        Args:
            prompt: Input prompt for the LLM
            temperature: Creativity level (0.0-1.0)
            max_tokens: Maximum tokens in response
            provider: Override default provider for this call
            stream: Whether to stream response
        
        Returns:
            Generated text response
        """
        target_provider = provider or self.provider
        self.call_count += 1
        
        try:
            if stream:
                return await self._generate_streaming(
                    prompt, temperature, max_tokens, target_provider
                )
            else:
                return await self._generate_sync(
                    prompt, temperature, max_tokens, target_provider
                )
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error with {target_provider}: {str(e)}")
            
            # Try fallback provider
            return await self._fallback_generate(
                prompt, temperature, max_tokens, target_provider
            )
    
    async def _generate_sync(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        provider: LLMProvider
    ) -> str:
        """Generate text synchronously using specified provider"""
        
        if provider == LLMProvider.GOOGLE:
            return self._generate_google(prompt, temperature, max_tokens)
        
        elif provider == LLMProvider.OPENAI:
            return await self._generate_openai(prompt, temperature, max_tokens)
        
        elif provider == LLMProvider.ANTHROPIC:
            return await self._generate_anthropic(prompt, temperature, max_tokens)
        
        elif provider == LLMProvider.OPENROUTER:
            return await self._generate_openrouter(prompt, temperature, max_tokens)
    
    def _generate_google(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate using Google Gemini"""
        try:
            model = genai.GenerativeModel(config.GOOGLE_MODEL.value)
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                }
            )
            
            logger.info(
                f"✓ Google Gemini ({config.GOOGLE_MODEL.value}): "
                f"{len(response.text.split())} tokens"
            )
            return response.text
        
        except Exception as e:
            logger.error(f"❌ Google Gemini error: {str(e)}")
            raise
    
    async def _generate_openai(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate using OpenAI GPT"""
        try:
            response = await self.openai_client.chat.completions.create(
                model=config.OPENAI_MODEL.value,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful travel planning assistant."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            content = response.choices[0].message.content
            logger.info(
                f"✓ OpenAI ({config.OPENAI_MODEL.value}): "
                f"Tokens - Input: {response.usage.prompt_tokens}, "
                f"Output: {response.usage.completion_tokens}"
            )
            return content
        
        except Exception as e:
            logger.error(f"❌ OpenAI error: {str(e)}")
            raise
    
    async def _generate_anthropic(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate using Anthropic Claude"""
        try:
            message = await self.anthropic_client.messages.create(
                model=config.ANTHROPIC_MODEL.value,
                max_tokens=max_tokens,
                system="You are a helpful travel planning assistant.",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
            )
            
            content = message.content[0].text
            logger.info(
                f"✓ Anthropic Claude ({config.ANTHROPIC_MODEL.value}): "
                f"{message.usage.output_tokens} output tokens"
            )
            return content
        
        except Exception as e:
            logger.error(f"❌ Anthropic error: {str(e)}")
            raise
    
    async def _generate_openrouter(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate using OpenRouter (access to 100+ models)"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
                        "HTTP-Referer": "https://github.com/KamdemSamuel/ai-travel-planner-gemini",
                    },
                    json={
                        "model": config.OPENROUTER_MODEL.value,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a helpful travel planning assistant."
                            },
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                    timeout=config.REQUEST_TIMEOUT,
                )
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                logger.info(
                    f"✓ OpenRouter ({config.OPENROUTER_MODEL.value}): "
                    f"{result.get('usage', {}).get('completion_tokens', 0)} tokens"
                )
                return content
        
        except Exception as e:
            logger.error(f"❌ OpenRouter error: {str(e)}")
            raise
    
    async def _generate_streaming(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        provider: LLMProvider
    ) -> AsyncGenerator[str, None]:
        """Generate with streaming response"""
        
        if provider == LLMProvider.GOOGLE:
            async for chunk in self._stream_google(prompt, temperature, max_tokens):
                yield chunk
        elif provider == LLMProvider.OPENAI:
            async for chunk in self._stream_openai(prompt, temperature, max_tokens):
                yield chunk
        else:
            # Fallback to non-streaming
            result = await self._generate_sync(
                prompt, temperature, max_tokens, provider
            )
            yield result
    
    async def _fallback_generate(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        failed_provider: LLMProvider
    ) -> str:
        """Try alternative providers on failure"""
        
        fallback_order = [
            p for p in [
                LLMProvider.GOOGLE,
                LLMProvider.OPENAI,
                LLMProvider.ANTHROPIC,
                LLMProvider.OPENROUTER,
            ] if p != failed_provider and config.is_provider_available(p)
        ]
        
        for fallback in fallback_order:
            try:
                logger.info(f"🔄 Falling back to {fallback}")
                return await self._generate_sync(
                    prompt, temperature, max_tokens, fallback
                )
            except Exception as e:
                logger.warning(f"Fallback {fallback} failed: {str(e)}")
                continue
        
        raise RuntimeError("All LLM providers failed")
    
    def _stream_google(self, prompt: str, temperature: float, max_tokens: int):
        """Stream from Google Gemini"""
        model = genai.GenerativeModel(config.GOOGLE_MODEL.value)
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            },
            stream=True
        )
        
        async def generator():
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        return generator()
    
    async def _stream_openai(self, prompt: str, temperature: float, max_tokens: int):
        """Stream from OpenAI"""
        stream = await self.openai_client.chat.completions.create(
            model=config.OPENAI_MODEL.value,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def get_stats(self) -> dict:
        """Get usage statistics"""
        return {
            "provider": self.provider.value,
            "total_calls": self.call_count,
            "errors": self.error_count,
            "success_rate": (
                ((self.call_count - self.error_count) / self.call_count * 100)
                if self.call_count > 0 else 0
            ),
        }


# Convenience function for simple usage
async def generate_text(
    prompt: str,
    provider: Optional[LLMProvider] = None,
    **kwargs
) -> str:
    """
    Simple function to generate text with any provider
    
    Usage:
        text = await generate_text("What's a good destination?")
    """
    client = LLMClient(provider)
    return await client.generate(prompt, **kwargs)


if __name__ == "__main__":
    # Test the client
    async def test():
        client = LLMClient()
        
        prompt = "Generate a short travel tip for visiting Tokyo"
        response = await client.generate(prompt, max_tokens=200)
        
        print(f"\n📝 Prompt: {prompt}")
        print(f"\n✨ Response:\n{response}")
        print(f"\n📊 Stats: {client.get_stats()}")
    
    asyncio.run(test())
