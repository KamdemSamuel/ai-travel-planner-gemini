"""
Main Application - Gradio Web Interface for AI Travel Planner
Provides interactive UI for travel itinerary generation
"""

import asyncio
import logging
from typing import Optional

import gradio as gr

from travel_planner import TravelPlanner
from config import LLMProvider, config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GradioTravelPlanner:
    """Gradio interface wrapper for travel planner"""
    
    def __init__(self):
        self.planner = None
        self.selected_provider = config.DEFAULT_PROVIDER
    
    def set_provider(self, provider_name: str):
        """Set the LLM provider"""
        try:
            self.selected_provider = LLMProvider(provider_name.lower())
            self.planner = TravelPlanner(provider=self.selected_provider)
            logger.info(f"✅ Provider changed to {provider_name}")
        except ValueError:
            logger.error(f"Invalid provider: {provider_name}")
    
    def generate_plan(
        self,
        destination: str,
        budget: str,
        days: int,
        interests: str,
        provider: str = ""
    ) -> str:
        """Generate travel itinerary"""
        
        # Validate inputs
        if not all([destination, budget, interests]):
            return "❌ Error: Please fill in all fields"
        
        try:
            days = int(days)
            if days < 1 or days > 30:
                return "❌ Error: Days must be between 1 and 30"
        except ValueError:
            return "❌ Error: Days must be a number"
        
        # Set provider if specified
        if provider and provider != "Auto":
            self.set_provider(provider)
        
        # Generate itinerary
        try:
            logger.info(f"Generating itinerary: {destination}, {days} days, {budget}")
            
            # Run async function
            itinerary = asyncio.run(
                self.planner.generate_itinerary(
                    destination=destination,
                    budget=budget,
                    days=days,
                    interests=interests
                )
            )
            
            return itinerary
        
        except Exception as e:
            error_msg = f"❌ Error generating itinerary: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def get_available_providers(self) -> list[str]:
        """Get list of available providers"""
        providers = ["Auto (Best Available)"]
        
        for provider in config.get_available_providers():
            providers.append(provider.value.upper())
        
        return providers


# Initialize
app = GradioTravelPlanner()
app.planner = TravelPlanner()  # Initialize with default


# ============================================================================
# GRADIO INTERFACE
# ============================================================================

with gr.Blocks(
    title="🌍 AI Travel Planner - Professional LLM Demo",
    theme=gr.themes.Soft(),
    css="""
        .header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            color: white;
            margin-bottom: 20px;
        }
        .info-box {
            background: #f0f0f0;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid #667eea;
        }
        .example-text {
            font-size: 12px;
            color: #666;
            font-style: italic;
        }
    """
) as demo:
    
    # Header
    gr.HTML("""
        <div class="header">
            <h1>🌍 AI Travel Planner - Professional LLM Integration Showcase</h1>
            <p>Generate personalized travel itineraries using advanced Large Language Models</p>
            <p style="font-size: 12px;">Supports: Google Gemini • OpenAI • Anthropic Claude • OpenRouter</p>
        </div>
    """)
    
    # Information section
    with gr.Group(label="ℹ️ About This Project"):
        gr.Markdown("""
        ### Professional LLM API Integration Demonstration
        
        This application showcases production-ready integration with multiple LLM providers:
        
        - **Google Gemini 2.0**: Fast, cost-effective, excellent for creative tasks
        - **OpenAI GPT-4**: Most capable for complex reasoning
        - **Anthropic Claude**: Best for structured outputs and long context
        - **OpenRouter**: Access to 100+ models with one API
        
        **Key Features:**
        - ✅ Multi-provider support with automatic fallback
        - ✅ Async/await for non-blocking API calls
        - ✅ Streaming support for real-time responses
        - ✅ Environment-based configuration
        - ✅ Error handling and retry logic
        - ✅ Production-ready code structure
        """)
    
    # Main interface
    with gr.Group(label="✈️ Generate Your Itinerary"):
        
        with gr.Row():
            with gr.Column(scale=2):
                destination = gr.Textbox(
                    label="📍 Destination",
                    placeholder="e.g., Tokyo, Japan",
                    info="Where do you want to travel?"
                )
                
                budget = gr.Textbox(
                    label="💰 Budget",
                    placeholder="e.g., $2000",
                    info="Total budget for the trip"
                )
            
            with gr.Column(scale=1):
                days = gr.Number(
                    label="📅 Days",
                    value=3,
                    minimum=1,
                    maximum=30,
                    step=1,
                    info="Trip duration"
                )
                
                provider = gr.Dropdown(
                    choices=app.get_available_providers(),
                    value="Auto (Best Available)",
                    label="🤖 LLM Provider",
                    info="Select preferred provider"
                )
        
        interests = gr.Textbox(
            label="🎯 Interests",
            placeholder="e.g., food, culture, hiking, museums",
            info="Comma-separated interests for personalized recommendations",
            lines=2
        )
        
        # Example usage
        gr.HTML("""
            <div class="info-box">
                <strong>💡 Example:</strong><br>
                Destination: <code>Paris, France</code> | Budget: <code>$1500</code> | 
                Days: <code>3</code> | Interests: <code>museums, food, architecture</code>
            </div>
        """)
        
        # Submit button
        submit_btn = gr.Button(
            "🚀 Generate Itinerary",
            variant="primary",
            size="lg"
        )
    
    # Output section
    output = gr.Textbox(
        label="✨ Your Personalized Itinerary",
        lines=15,
        max_lines=20,
        interactive=False,
        show_copy_button=True
    )
    
    # Status/Info section
    with gr.Group(label="📊 Generation Info"):
        status = gr.Textbox(
            label="Status",
            interactive=False,
            value="Ready to generate itineraries"
        )
    
    # Technical details
    with gr.Accordion(label="🔧 Technical Details & Code Examples", open=False):
        gr.Markdown("""
        ### How This Works
        
        **1. Multi-Provider Architecture:**
        ```python
        from llm_client import LLMClient
        from config import LLMProvider
        
        client = LLMClient(provider=LLMProvider.GOOGLE)
        response = await client.generate(prompt, max_tokens=2000)
        ```
        
        **2. Provider Abstraction:**
        The system provides a unified interface across all providers:
        - Automatically handles API differences
        - Implements fallback logic on failures
        - Tracks usage and errors
        
        **3. Async/Await Support:**
        ```python
        async def generate_plan(destination, budget, days, interests):
            planner = TravelPlanner()
            return await planner.generate_itinerary(
                destination, budget, days, interests
            )
        ```
        
        **4. Configuration Management:**
        - Environment variables via `.env` file
        - Dynamic provider selection
        - Secure API key handling
        
        ### Project Structure
        ```
        ├── main.py              # This Gradio UI
        ├── travel_planner.py    # Core logic
        ├── llm_client.py        # Multi-provider abstraction
        ├── config.py            # Configuration management
        ├── prompts.py           # Optimized prompt templates
        └── requirements.txt     # Dependencies
        ```
        
        ### Skills Demonstrated
        - ✅ LLM API Integration (Google, OpenAI, Anthropic, OpenRouter)
        - ✅ Async Programming (asyncio, await)
        - ✅ Error Handling & Fallback Logic
        - ✅ Configuration Management
        - ✅ Web UI Development (Gradio)
        - ✅ Production Code Patterns
        """)
    
    # Examples section
    with gr.Accordion(label="📚 Example Destinations", open=False):
        gr.Examples(
            examples=[
                ["Tokyo, Japan", "$1500", 5, "temples, food, technology"],
                ["Paris, France", "$2000", 3, "museums, food, architecture"],
                ["Bali, Indonesia", "$800", 4, "beaches, culture, yoga"],
                ["New York, USA", "$2500", 4, "museums, food, Broadway"],
                ["Barcelona, Spain", "$1200", 3, "architecture, beaches, food"],
            ],
            inputs=[destination, budget, days, interests],
            outputs=output,
            fn=app.generate_plan,
            cache_examples=False,
        )
    
    # Footer
    gr.HTML("""
        <div style="text-align: center; margin-top: 30px; padding: 20px; 
                    background: #f9f9f9; border-radius: 8px; border-top: 2px solid #ddd;">
            <p><strong>🎓 Portfolio Project by Kamdem Samuel Yedidya</strong></p>
            <p>
                <a href="https://github.com/KamdemSamuel/ai-travel-planner-gemini" 
                   target="_blank" style="margin: 0 10px;">GitHub</a> •
                <a href="https://linkedin.com/in/samuel-yedidya-tchuenche-kamdem-9b651034a/" 
                   target="_blank" style="margin: 0 10px;">LinkedIn</a>
            </p>
            <p style="font-size: 12px; color: #666; margin-top: 15px;">
                This project demonstrates professional LLM API integration with multi-provider support,
                async programming, and production-ready code patterns.
            </p>
        </div>
    """)
    
    # Connect button to function
    submit_btn.click(
        fn=app.generate_plan,
        inputs=[destination, budget, days, interests, provider],
        outputs=[output, status],
        api_name="generate",
    )


# ============================================================================
# MAIN - LAUNCH APP
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🌍 AI TRAVEL PLANNER - LAUNCHING GRADIO INTERFACE")
    print("=" * 70)
    print("\n✨ Starting web server...")
    print(f"📍 Available providers: {', '.join(config.get_available_providers())}")
    print(f"🤖 Default provider: {config.DEFAULT_PROVIDER.value.upper()}\n")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )
