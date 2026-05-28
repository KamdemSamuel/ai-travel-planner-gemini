"""
Prompt Templates for Travel Planning
Optimized for different LLM providers and use cases
"""

from typing import Dict, Any
from config import LLMProvider


class PromptTemplate:
    """Base prompt template"""
    
    def __init__(self, template: str):
        self.template = template
    
    def format(self, **kwargs) -> str:
        """Format template with provided variables"""
        return self.template.format(**kwargs)


# ============================================================================
# MAIN ITINERARY GENERATION PROMPTS
# ============================================================================

ITINERARY_GENERATION = {
    "google": PromptTemplate("""
You are an expert travel planner AI. Create a detailed, personalized {days}-day travel itinerary.

**Destination:** {destination}
**Total Budget:** {budget}
**Interests:** {interests}

Please structure your response as follows:

**Day 1: [Day Title]**
- Morning: [Activity] (Estimated cost: $XX)
  💡 Insider tip: [Local advice]
- Afternoon: [Activity] (Estimated cost: $XX)
- Evening: [Activity] (Estimated cost: $XX)

Estimated Daily Budget: $XX

**Pro Tip:** [Helpful advice for the day]

---

Repeat for each day. At the end, include:
- Total estimated budget breakdown
- Money-saving tips
- Best times to visit
- Important travel notes

Make it engaging with emojis and specific recommendations based on local expertise.
"""),
    
    "openai": PromptTemplate("""
As an expert travel advisor, generate a {days}-day detailed itinerary.

Input Details:
- Destination: {destination}
- Budget: {budget}
- Interests: {interests}

Output Format:
For each day, provide:
1. Morning activity with estimated cost
2. Afternoon activity with estimated cost  
3. Evening activity with estimated cost
4. Daily budget summary
5. Insider tip

Include:
- Specific restaurant/venue recommendations where applicable
- Cost estimates for food, activities, transport
- Best time to do each activity
- Local tips for better experience

End with total trip budget and money-saving recommendations.
Be specific and practical in recommendations.
"""),
    
    "anthropic": PromptTemplate("""
Generate a comprehensive {days}-day travel itinerary.

**Context:**
- Destination: {destination}
- Budget: {budget}
- Traveler interests: {interests}

**Requirements:**
1. Daily breakdown with morning/afternoon/evening activities
2. Realistic cost estimates for each activity
3. Insider tips from local knowledge
4. Pro tips for budget optimization
5. Best times and seasons to visit
6. Cultural notes and local customs

**Output Structure:**
[Day number]: [Theme]
├── Morning: [Activity] - $[cost]
├── Afternoon: [Activity] - $[cost]
├── Evening: [Activity] - $[cost]
└── Daily Total: $[cost]

Provide practical, verified recommendations only.
Include contingency suggestions for bad weather or changes.
"""),
    
    "openrouter": PromptTemplate("""
Create a {days}-day travel plan for {destination}.

Trip Details:
- Budget: {budget}
- Duration: {days} days
- Interests: {interests}

Please provide:
1. Daily itineraries with 3 main activities
2. Realistic cost breakdown (food, attractions, transport)
3. Insider recommendations (local spots, not tourist traps)
4. Pro tips for each day
5. Total budget summary with savings suggestions

Format each day clearly with times and estimated costs.
Include cultural tips and best practices.
Keep recommendations practical and achievable.
"""),
}


# ============================================================================
# BUDGET OPTIMIZATION PROMPTS
# ============================================================================

BUDGET_OPTIMIZATION = {
    "default": PromptTemplate("""
Optimize this travel plan to fit within the budget of {budget}.

Current Plan Details:
{current_plan}

Please provide:
1. Budget-friendly alternatives for each activity
2. Money-saving tips specific to {destination}
3. Free or low-cost attractions
4. Best value restaurants and accommodation
5. When to visit to save money (seasons/days)
6. Transport optimization suggestions

Maintain the quality and experience while reducing costs.
"""),
}


# ============================================================================
# DESTINATION INFO PROMPTS
# ============================================================================

DESTINATION_INFO = {
    "default": PromptTemplate("""
Provide brief essential information about {destination}.

Include:
1. Best time to visit
2. Weather/climate information
3. Currency and typical costs
4. Language tips
5. Must-see attractions (top 3)
6. Best neighborhoods to stay in
7. Getting around (transport options)
8. Safety tips
9. Cultural etiquette
10. Quick travel hack

Keep it concise and practical.
"""),
}


# ============================================================================
# ACTIVITY RECOMMENDATION PROMPTS
# ============================================================================

ACTIVITY_RECOMMENDATIONS = {
    "default": PromptTemplate("""
Recommend {activity_count} unique activities in {destination} for someone interested in: {interests}

For each activity, provide:
1. Activity name and description
2. Best time to visit
3. Estimated cost
4. How to get there
5. Insider tip or what makes it special
6. How long it takes

Format as a numbered list with practical details.
Focus on experiences that match the stated interests.
"""),
}


# ============================================================================
# COST BREAKDOWN PROMPTS
# ============================================================================

COST_BREAKDOWN = {
    "default": PromptTemplate("""
Create a detailed cost breakdown for a {days}-day trip to {destination}.

Budget: {budget}

Provide:
1. Accommodation costs by type (budget/mid-range/luxury)
2. Food budget (breakfast, lunch, dinner ranges)
3. Activity costs (museums, tours, experiences)
4. Transport within city
5. Miscellaneous/shopping budget
6. Emergency fund recommendation

Show breakdown as percentages and specific amounts.
Include both budget and mid-range options.
"""),
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_itinerary_prompt(
    destination: str,
    budget: str,
    days: str,
    interests: str,
    provider: LLMProvider = LLMProvider.GOOGLE
) -> str:
    """
    Get optimized itinerary prompt for specific provider
    
    Args:
        destination: Travel destination
        budget: Budget as string (e.g., "$2000")
        days: Number of days as string
        interests: Comma-separated interests
        provider: LLM provider to optimize for
    
    Returns:
        Formatted prompt string
    """
    prompt_template = ITINERARY_GENERATION.get(
        provider.value,
        ITINERARY_GENERATION["google"]  # Fallback
    )
    
    return prompt_template.format(
        destination=destination,
        budget=budget,
        days=days,
        interests=interests
    )


def get_optimization_prompt(
    destination: str,
    budget: str,
    current_plan: str
) -> str:
    """Get budget optimization prompt"""
    return BUDGET_OPTIMIZATION["default"].format(
        destination=destination,
        budget=budget,
        current_plan=current_plan
    )


def get_destination_prompt(destination: str) -> str:
    """Get destination info prompt"""
    return DESTINATION_INFO["default"].format(destination=destination)


def get_activities_prompt(
    destination: str,
    interests: str,
    activity_count: int = 5
) -> str:
    """Get activity recommendations prompt"""
    return ACTIVITY_RECOMMENDATIONS["default"].format(
        destination=destination,
        interests=interests,
        activity_count=activity_count
    )


def get_cost_prompt(
    destination: str,
    budget: str,
    days: str
) -> str:
    """Get cost breakdown prompt"""
    return COST_BREAKDOWN["default"].format(
        destination=destination,
        budget=budget,
        days=days
    )


# Prompt optimization tips by provider
PROVIDER_TIPS = {
    LLMProvider.GOOGLE: {
        "max_tokens": 3000,
        "temperature": 0.7,
        "style": "Gemini works great with structured formats and emoji",
        "best_for": "Travel planning, creative content",
    },
    LLMProvider.OPENAI: {
        "max_tokens": 2000,
        "temperature": 0.7,
        "style": "GPT excels at detailed reasoning and nuance",
        "best_for": "Complex decision-making, detailed explanations",
    },
    LLMProvider.ANTHROPIC: {
        "max_tokens": 2000,
        "temperature": 0.5,
        "style": "Claude prefers clear structure and context",
        "best_for": "Long-form content, accuracy-focused tasks",
    },
    LLMProvider.OPENROUTER: {
        "max_tokens": 2000,
        "temperature": 0.7,
        "style": "Flexible - depends on underlying model",
        "best_for": "Model experimentation, cost optimization",
    },
}


if __name__ == "__main__":
    # Test prompt generation
    print("Testing Prompt Templates:")
    print("=" * 60)
    
    prompt = get_itinerary_prompt(
        destination="Paris, France",
        budget="$1500",
        days="3",
        interests="museums, food, architecture",
        provider=LLMProvider.GOOGLE
    )
    
    print(prompt)
