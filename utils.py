"""
Utility Functions - Formatting, validation, and helper functions
"""

import re
from typing import Optional, Dict, Any
from datetime import datetime


class ItineraryFormatter:
    """Format itinerary content for better presentation"""
    
    @staticmethod
    def add_emojis(text: str) -> str:
        """Add emojis to enhance readability"""
        text = re.sub(r'Day (\d+):', r'✨ Day \1:', text)
        text = re.sub(r'\bMorning:', r'🕘 Morning:', text, flags=re.IGNORECASE)
        text = re.sub(r'\bAfternoon:', r'🕐 Afternoon:', text, flags=re.IGNORECASE)
        text = re.sub(r'\bEvening:', r'🌙 Evening:', text, flags=re.IGNORECASE)
        text = re.sub(r'Insider tip:', r'💡 Insider Tip:', text, flags=re.IGNORECASE)
        text = re.sub(r'Pro tip:', r'🌟 Pro Tip:', text, flags=re.IGNORECASE)
        text = re.sub(r'Budget:', r'💰 Budget:', text, flags=re.IGNORECASE)
        text = re.sub(r'Cost:', r'💵 Cost:', text, flags=re.IGNORECASE)
        text = re.sub(r'(\$[\d,]+\.?\d*)', r'💲 \1', text)
        text = re.sub(r'Transport:', r'🚕 Transport:', text, flags=re.IGNORECASE)
        text = re.sub(r'Food:', r'🍽️ Food:', text, flags=re.IGNORECASE)
        text = re.sub(r'Accommodation:', r'🏨 Accommodation:', text, flags=re.IGNORECASE)
        return text
    
    @staticmethod
    def clean_markdown(text: str) -> str:
        """Remove or convert markdown formatting"""
        # Remove bold
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        # Remove italic
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        # Remove code blocks
        text = re.sub(r'```(.+?)```', r'\1', text, flags=re.DOTALL)
        # Convert headers
        text = re.sub(r'#+\s+', '', text)
        return text
    
    @staticmethod
    def add_header(
        destination: str,
        days: int,
        budget: str,
        provider: str
    ) -> str:
        """Generate a formatted header"""
        header = "\n" + "=" * 70 + "\n"
        header += "🌍 AI TRAVEL ITINERARY - PROFESSIONAL LLM INTEGRATION\n"
        header += "=" * 70 + "\n\n"
        header += f"📍 Destination: {destination}\n"
        header += f"📅 Duration: {days} days\n"
        header += f"💰 Budget: {budget}\n"
        header += f"🤖 Generated with: {provider.upper()}\n"
        header += f"⏰ Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += "\n" + "-" * 70 + "\n\n"
        return header


class InputValidator:
    """Validate user inputs"""
    
    @staticmethod
    def validate_destination(destination: str) -> bool:
        """Validate destination input"""
        if not destination or not isinstance(destination, str):
            return False
        if len(destination.strip()) < 2:
            return False
        return True
    
    @staticmethod
    def validate_budget(budget: str) -> bool:
        """Validate budget input"""
        if not budget or not isinstance(budget, str):
            return False
        # Extract number from budget string
        numbers = re.findall(r'\d+', budget)
        if not numbers:
            return False
        amount = int(numbers[0])
        return 1 <= amount <= 1000000  # Between $1 and $1M
    
    @staticmethod
    def validate_days(days: int) -> bool:
        """Validate days input"""
        if not isinstance(days, (int, float)):
            return False
        days_int = int(days)
        return 1 <= days_int <= 365
    
    @staticmethod
    def validate_interests(interests: str) -> bool:
        """Validate interests input"""
        if not interests or not isinstance(interests, str):
            return False
        if len(interests.strip()) < 3:
            return False
        return True
    
    @staticmethod
    def validate_all(
        destination: str,
        budget: str,
        days: int,
        interests: str
    ) -> tuple[bool, Optional[str]]:
        """Validate all inputs together"""
        if not InputValidator.validate_destination(destination):
            return False, "Invalid destination"
        if not InputValidator.validate_budget(budget):
            return False, "Invalid budget (must be $1-$1,000,000)"
        if not InputValidator.validate_days(days):
            return False, "Invalid days (must be 1-365)"
        if not InputValidator.validate_interests(interests):
            return False, "Invalid interests"
        return True, None


class CostCalculator:
    """Calculate and estimate costs"""
    
    @staticmethod
    def extract_costs(text: str) -> list[float]:
        """Extract all costs from text"""
        pattern = r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'
        matches = re.findall(pattern, text)
        return [float(m.replace(',', '')) for m in matches]
    
    @staticmethod
    def calculate_total_budget(text: str) -> float:
        """Calculate total budget from itinerary"""
        costs = CostCalculator.extract_costs(text)
        return sum(costs) if costs else 0.0
    
    @staticmethod
    def estimate_daily_average(total: float, days: int) -> float:
        """Calculate daily average spend"""
        return total / days if days > 0 else 0.0
    
    @staticmethod
    def format_currency(amount: float, currency: str = "USD") -> str:
        """Format amount as currency"""
        symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥",
            "CAD": "C$",
            "AUD": "A$",
        }
        symbol = symbols.get(currency, "$")
        return f"{symbol}{amount:,.2f}"


class TextAnalyzer:
    """Analyze text content"""
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    @staticmethod
    def count_sentences(text: str) -> int:
        """Count sentences in text"""
        return len(re.split(r'[.!?]+', text)) - 1
    
    @staticmethod
    def count_days(text: str) -> int:
        """Extract number of days from text"""
        pattern = r'Day (\d+)'
        matches = re.findall(pattern, text)
        return max([int(m) for m in matches]) if matches else 0
    
    @staticmethod
    def extract_activities(text: str) -> list[str]:
        """Extract activity names from text"""
        # Look for patterns like "- Activity Name"
        pattern = r'(?:^|\n)\s*[-•*]\s*([A-Z][^:]*)'
        matches = re.findall(pattern, text, re.MULTILINE)
        return list(dict.fromkeys(matches))  # Remove duplicates while preserving order
    
    @staticmethod
    def get_summary_stats(text: str) -> Dict[str, Any]:
        """Get comprehensive text analysis"""
        return {
            "word_count": TextAnalyzer.count_words(text),
            "sentence_count": TextAnalyzer.count_sentences(text),
            "days": TextAnalyzer.count_days(text),
            "activities": TextAnalyzer.extract_activities(text),
            "character_count": len(text),
        }


# Convenience functions
def validate_travel_input(
    destination: str,
    budget: str,
    days: int,
    interests: str
) -> tuple[bool, Optional[str]]:
    """Quick validation of travel input"""
    return InputValidator.validate_all(destination, budget, days, interests)


def format_itinerary_complete(
    text: str,
    destination: str,
    days: int,
    budget: str,
    provider: str
) -> str:
    """Format complete itinerary with header and emoji"""
    formatter = ItineraryFormatter()
    header = formatter.add_header(destination, days, budget, provider)
    cleaned = formatter.clean_markdown(text)
    with_emojis = formatter.add_emojis(cleaned)
    return header + with_emojis


def analyze_itinerary(text: str) -> Dict[str, Any]:
    """Analyze itinerary content"""
    analyzer = TextAnalyzer()
    calculator = CostCalculator()
    
    stats = analyzer.get_summary_stats(text)
    costs = calculator.extract_costs(text)
    total = calculator.calculate_total_budget(text)
    
    return {
        **stats,
        "total_estimated_cost": total,
        "daily_average_cost": (
            calculator.estimate_daily_average(total, stats["days"])
            if stats["days"] > 0 else 0
        ),
        "individual_costs": costs,
        "cost_count": len(costs),
    }


if __name__ == "__main__":
    # Test utilities
    sample_text = """
    Day 1: Tokyo Highlights
    - Morning: Visit Senso-ji Temple (Cost: $10)
      Insider Tip: Go early to avoid crowds
    - Afternoon: Explore Shibuya Crossing (Cost: $0)
    - Evening: Dinner at local restaurant (Cost: $25)
    
    Total Day 1: $35
    """
    
    print("Testing Utilities:")
    print("=" * 60)
    
    # Test formatter
    formatter = ItineraryFormatter()
    formatted = formatter.add_emojis(sample_text)
    print("Formatted with emojis:")
    print(formatted)
    
    # Test analyzer
    analyzer = TextAnalyzer()
    stats = analyzer.get_summary_stats(sample_text)
    print(f"\n\nText Analysis:")
    print(f"  Words: {stats['word_count']}")
    print(f"  Days: {stats['days']}")
    print(f"  Activities found: {stats['activities']}")
    
    # Test calculator
    calculator = CostCalculator()
    costs = calculator.extract_costs(sample_text)
    print(f"\n\nCost Analysis:")
    print(f"  Costs found: {costs}")
    print(f"  Total: {calculator.format_currency(sum(costs))}")
