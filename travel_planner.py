"""
Core Travel Planner Logic
Generates personalized travel itineraries using LLM APIs
"""

import asyncio
import logging
import re
from typing import Optional, AsyncGenerator
from datetime import datetime

from llm_client import LLMClient
from config import LLMProvider, config, TEMPERATURE_PRESETS
from prompts import get_itinerary_prompt, get_destination_prompt, get_activities_prompt

logger = logging.getLogger(__name__)


class TravelPlanner:
    """Main travel planner class"""
    
    def __init__(self, provider: Optional[LLMProvider] = None):
        """
        Initialize Travel Planner
        
        Args:
            provider: Preferred LLM provider
        """
        self.provider = provider or config.DEFAULT_PROVIDER
        self.llm_client = LLMClient(provider)
        logger.info(f"🌍 Travel Planner initialized with {self.provider}")
    
    async def generate_itinerary(
        self,
        destination: str,
        budget: str,
        days: int,
        interests: str,
        stream: bool = False
    ) -> str | AsyncGenerator[str, None]:
        """
        Generate a personalized travel itinerary
        
        Args:
            destination: Travel destination
            budget: Budget string (e.g., "$2000")
            days: Number of days for trip
            interests: Comma-separated interests (e.g., "food, culture, hiking")
            stream: Whether to stream response
        
        Returns:
            Generated itinerary as string or async generator for streaming
        """
        # Validate inputs
        if not all([destination, budget, days, interests]):
            raise ValueError("All fields (destination, budget, days, interests) are required")
        
        if not isinstance(days, int) or days < 1:
            raise ValueError("Days must be a positive integer")
        
        # Get optimized prompt
        prompt = get_itinerary_prompt(
            destination=destination,
            budget=budget,
            days=str(days),
            interests=interests,
            provider=self.provider
        )
        
        logger.info(f"📍 Generating itinerary for {destination} ({days} days, {budget})")
        
        # Generate content
        response = await self.llm_client.generate(
            prompt=prompt,
            temperature=TEMPERATURE_PRESETS["balanced"],
            max_tokens=3000,
            provider=self.provider,
            stream=stream
        )
        
        if stream:
            return response  # AsyncGenerator
        else:
            # Format response
            formatted = self._format_itinerary(response)
            return formatted
    
    async def generate_itinerary_with_fallback(
        self,
        destination: str,
        budget: str,
        days: int,
        interests: str,
    ) -> str:
        """
        Generate itinerary with automatic fallback to other providers
        
        Args:
            destination: Travel destination
            budget: Budget string
            days: Number of days
            interests: Comma-separated interests
        
        Returns:
            Generated itinerary
        """
        try:
            result = await self.generate_itinerary(
                destination, budget, days, interests
            )
            return result
        except Exception as e:
            logger.error(f"❌ Primary provider failed: {str(e)}")
            logger.info("🔄 Attempting fallback providers...")
            
            # Try alternative providers
            for alt_provider in [LLMProvider.OPENAI, LLMProvider.ANTHROPIC, LLMProvider.GOOGLE]:
                if alt_provider == self.provider:
                    continue
                
                if not config.is_provider_available(alt_provider):
                    continue
                
                try:
                    logger.info(f"Trying {alt_provider}...")
                    fallback_planner = TravelPlanner(provider=alt_provider)
                    result = await fallback_planner.generate_itinerary(
                        destination, budget, days, interests
                    )
                    return result
                except Exception as e:
                    logger.warning(f"  {alt_provider} failed: {str(e)}")
                    continue
            
            raise RuntimeError("All LLM providers failed")
    
    async def get_destination_info(self, destination: str) -> str:
        """
        Get quick info about a destination
        
        Args:
            destination: Destination name
        
        Returns:
            Destination information
        """
        prompt = get_destination_prompt(destination)
        
        response = await self.llm_client.generate(
            prompt=prompt,
            temperature=TEMPERATURE_PRESETS["precise"],
            max_tokens=1000,
            provider=self.provider
        )
        
        return response
    
    async def get_activity_recommendations(
        self,
        destination: str,
        interests: str,
        activity_count: int = 5
    ) -> str:
        """
        Get activity recommendations for a destination
        
        Args:
            destination: Destination name
            interests: Comma-separated interests
            activity_count: Number of activities to recommend
        
        Returns:
            Recommended activities
        """
        prompt = get_activities_prompt(destination, interests, activity_count)
        
        response = await self.llm_client.generate(
            prompt=prompt,
            temperature=TEMPERATURE_PRESETS["creative"],
            max_tokens=1500,
            provider=self.provider
        )
        
        return response
    
    def _format_itinerary(self, text: str) -> str:
        """
        Format raw itinerary text for better presentation
        
        Args:
            text: Raw LLM response
        
        Returns:
            Formatted itinerary
        """
        # Add emoji formatting
        text = re.sub(r'\*\*', '', text)  # Remove markdown bold
        text = re.sub(r'Day (\d+):', r'\n✨ Day \1:', text)
        text = re.sub(r'(Morning|Afternoon|Evening):', r'🕘 \1:', text)
        text = re.sub(r'Insider [Tt]ip:', '💡 Insider Tip:', text)
        text = re.sub(r'Pro [Tt]ip:', '🌟 Pro Tip:', text)
        text = re.sub(r'(\$[\d,]+)', r'💰 \1', text)
        
        # Add header
        header = "\n" + "=" * 60 + "\n"
        header += "          🌍 AI TRAVEL ITINERARY (POWERED BY LLM)       \n"
        header += "=" * 60 + "\n"
        
        timestamp = f"\n📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        provider_info = f"🤖 Provider: {self.provider.value.upper()}\n"
        
        return header + provider_info + timestamp + text
    
    def save_itinerary(self, itinerary: str, filename: str = None) -> str:
        """
        Save itinerary to file
        
        Args:
            itinerary: Itinerary text
            filename: Output filename (auto-generated if None)
        
        Returns:
            Filepath where itinerary was saved
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"itinerary_{timestamp}.txt"
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(itinerary)
            logger.info(f"✅ Itinerary saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"❌ Failed to save itinerary: {str(e)}")
            raise
    
    def get_client_stats(self) -> dict:
        """Get LLM client usage statistics"""
        return self.llm_client.get_stats()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def quick_plan(
    destination: str,
    budget: str,
    days: int,
    interests: str,
    provider: Optional[LLMProvider] = None
) -> str:
    """
    Quick way to generate an itinerary
    
    Usage:
        itinerary = await quick_plan(
            "Tokyo, Japan",
            "$2000",
            5,
            "food, temples, museums"
        )
    """
    planner = TravelPlanner(provider=provider)
    return await planner.generate_itinerary(
        destination, budget, days, interests
    )


async def stream_plan(
    destination: str,
    budget: str,
    days: int,
    interests: str,
    provider: Optional[LLMProvider] = None
) -> AsyncGenerator[str, None]:
    """
    Stream an itinerary generation
    
    Usage:
        async for chunk in stream_plan(...):
            print(chunk, end="", flush=True)
    """
    planner = TravelPlanner(provider=provider)
    return await planner.generate_itinerary(
        destination, budget, days, interests, stream=True
    )


# ============================================================================
# MAIN - Test functionality
# ============================================================================

async def main():
    """Test the travel planner"""
    
    planner = TravelPlanner()
    
    print("\n🌍 AI Travel Planner Demo")
    print("=" * 60)
    
    # Example itinerary
    itinerary = await planner.generate_itinerary(
        destination="Bali, Indonesia",
        budget="$1000",
        days=3,
        interests="beaches, temples, food"
    )
    
    print(itinerary)
    
    # Save itinerary
    filepath = planner.save_itinerary(itinerary)
    print(f"\n✅ Saved to: {filepath}")
    
    # Show stats
    stats = planner.get_client_stats()
    print(f"\n📊 Stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
