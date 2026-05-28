# 🌍 AI Travel Planner - Professional LLM Integration Showcase

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![LLM Support](https://img.shields.io/badge/LLM%20Support-Google%20%7C%20OpenAI%20%7C%20Anthropic%20%7C%20OpenRouter-FF6B6B)](https://github.com/KamdemSamuel/ai-travel-planner-gemini)

**An enterprise-grade AI-powered travel itinerary generator demonstrating professional Large Language Model API integration across multiple providers.**

*By Kamdem Samuel Yedidya* | [LinkedIn](https://www.linkedin.com/in/samuel-yedidya-tchuenche-kamdem-9b651034a/)

---

## 🎯 Project Highlights

This project demonstrates **production-ready LLM API integration** with:

✅ **Multi-LLM Support** - Seamlessly switch between Google Gemini, OpenAI GPT, Anthropic Claude, OpenRouter  
✅ **Enterprise Architecture** - Modular design with separation of concerns  
✅ **Error Handling & Fallbacks** - Robust retry logic and provider failover  
✅ **Environment Management** - Secure API key handling via `.env`  
✅ **Real-time Streaming** - Support for token streaming with multiple LLMs  
✅ **Caching Layer** - Optimize costs and reduce latency  
✅ **Interactive UI** - Gradio interface for production deployment  
✅ **Portfolio-Ready Code** - Industry standards with documentation  

---

## 🚀 Features

### Core Functionality
- 🗺️ **Intelligent Itinerary Generation** - AI-powered daily travel plans
- 💰 **Budget Optimization** - Cost breakdowns and money-saving tips
- 🎯 **Interest-Based Planning** - Customized activities (food, culture, adventure, etc.)
- 🌟 **Local Insights** - Insider tips and hidden gems
- 📱 **Web UI** - Easy-to-use Gradio interface
- 📄 **Export to File** - Save itineraries as formatted documents

### Technical Excellence
- **LLM Provider Abstraction** - Unified interface across multiple AI APIs
- **Configuration Management** - Dynamic provider switching
- **Prompt Engineering** - Optimized templates for consistent results
- **Type Hints** - Full Python typing for maintainability
- **Async Support** - Non-blocking API calls
- **Unit Tests** - Comprehensive test coverage

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **LLM APIs** | Google Gemini 2.0, OpenAI GPT-4, Anthropic Claude 3, OpenRouter |
| **Python** | 3.10+ with async/await, type hints |
| **UI Framework** | Gradio 4.x |
| **Config** | Python-dotenv, Pydantic |
| **HTTP Client** | httpx (async-first) |
| **Data Processing** | Pandas, regex |

---

## 📋 Getting Started

### Prerequisites
```bash
Python 3.10+
pip or conda
API keys for at least one LLM provider
```

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/KamdemSamuel/ai-travel-planner-gemini.git
   cd ai-travel-planner-gemini
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API keys**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

### Configuration (.env)
```env
# At least one provider is required

# Google Gemini
GOOGLE_API_KEY=your_google_api_key_here

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo

# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# OpenRouter (access to multiple models)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Default provider to use
DEFAULT_LLM_PROVIDER=google  # Options: google, openai, anthropic, openrouter
```

---

## 💻 Quick Start

### Run the Web Interface
```bash
python main.py
```
Launches Gradio UI at `http://localhost:7860`

### Use Programmatically
```python
from travel_planner import TravelPlanner
from config import LLMProvider

# Initialize with desired provider
planner = TravelPlanner(provider=LLMProvider.GOOGLE)

# Generate itinerary
itinerary = planner.generate_itinerary(
    destination="Tokyo, Japan",
    budget="$2000",
    days=5,
    interests="food, culture, temples"
)

print(itinerary)
```

### API Provider Switching
```python
from travel_planner import TravelPlanner
from config import LLMProvider

# Automatically switches provider based on availability
planner = TravelPlanner(provider=LLMProvider.ANTHROPIC)

# If Claude API fails, falls back to OpenAI, then Google
itinerary = planner.generate_itinerary_with_fallback(
    destination="Paris",
    budget="$1500",
    days=3,
    interests="museums, wine, pastries"
)
```

---

## 📁 Project Structure

```
ai-travel-planner-gemini/
├── main.py                 # Entry point - Gradio UI
├── travel_planner.py       # Core travel planner logic
├── llm_client.py           # LLM API abstraction layer
├── config.py               # Configuration & environment management
├── prompts.py              # Prompt templates for each LLM
├── utils.py                # Helper functions & formatting
├── requirements.txt        # Python dependencies
├── .env.example             # Example environment file
├── README.md               # This file
├── LICENSE                 # MIT License
└── notebooks/
    └── ai-travel-assistant.ipynb  # Jupyter notebook demo
```

---

## 🔧 Architecture

### LLM Client Abstraction
The `llm_client.py` module provides a **unified interface** to all LLM providers:

```python
class LLMClient:
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> str:
        """Unified interface across all LLM providers"""
```

**Supported Providers:**
- 🔵 **Google Gemini** - Fast, affordable, streaming support
- 🟢 **OpenAI GPT** - Most capable, great for complex reasoning
- 🟪 **Anthropic Claude** - Best for structured outputs, long context
- 🔀 **OpenRouter** - Access to 100+ models through one API

### Provider Selection Logic
1. Attempts primary provider from `DEFAULT_LLM_PROVIDER`
2. Falls back to next available provider on error
3. Logs all API calls for debugging
4. Implements exponential backoff for rate limiting

---

## 🎓 LLM Integration Examples

### Google Gemini (Primary Provider)
```python
import google.generativeai as genai

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Streaming response
response = model.generate_content(prompt, stream=True)
for chunk in response:
    print(chunk.text, end="", flush=True)
```

### OpenAI GPT-4
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

response = await client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
    max_tokens=2000
)
```

### Anthropic Claude
```python
import anthropic

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

message = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=2000,
    messages=[{"role": "user", "content": prompt}]
)
```

### OpenRouter (Multi-Model Access)
```python
response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
    json={
        "model": "anthropic/claude-3-sonnet",  # Can switch models
        "messages": [{"role": "user", "content": prompt}]
    }
)
```

---

## 🧪 Testing & Validation

### Run Tests
```bash
pytest tests/ -v
```

### Test Coverage
```bash
pytest tests/ --cov=travel_planner --cov-report=html
```

---

## 📊 Performance & Costs

| Provider | Speed | Cost (per 1K tokens) | Best For |
|----------|-------|---------------------|----------|
| Google Gemini | ⚡ Fast | $0.075 in | Budget-friendly |
| OpenAI GPT-4 | 🟡 Medium | $0.03 in, $0.06 out | Complex reasoning |
| Claude 3 Sonnet | 🟡 Medium | $0.003 in | Long context |
| OpenRouter | 🟢 Varies | Depends on model | Model flexibility |

---

## 🔐 Security Best Practices

✅ **API Keys**: Never commit `.env` files - use `python-dotenv`  
✅ **Rate Limiting**: Implemented exponential backoff  
✅ **Input Validation**: Sanitize user inputs before API calls  
✅ **Error Messages**: Never expose API keys in error logs  
✅ **Environment Isolation**: Different keys for dev/prod  

---

## 🚀 Deployment Options

### Option 1: Docker
```bash
docker build -t travel-planner .
docker run -p 7860:7860 --env-file .env travel-planner
```

### Option 2: Hugging Face Spaces
```bash
gradio deploy
```

### Option 3: AWS Lambda + API Gateway
Configured for serverless deployment with async handlers.

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- [ ] Add hotel recommendations API
- [ ] Weather forecast integration
- [ ] Real-time flight price checking
- [ ] Multi-language support
- [ ] Vision API for image-based travel uploads

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 📚 References & Resources

### Official Documentation
- [Google Generative AI API](https://ai.google.dev/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [OpenRouter API](https://openrouter.ai/docs)

### Best Practices
- [Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [LLM API Rate Limiting](https://platform.openai.com/docs/guides/rate-limits)
- [Async Programming in Python](https://docs.python.org/3/library/asyncio.html)

---

## 🎯 Skills Demonstrated

This portfolio project showcases:

✅ **LLM API Integration** - Multi-provider support with fallback logic  
✅ **Cloud Architecture** - Scalable design patterns  
✅ **Python Best Practices** - Type hints, async/await, error handling  
✅ **API Design** - Clean abstractions, documentation  
✅ **DevOps** - Docker, environment management, deployment  
✅ **Testing** - Unit tests, integration tests, coverage reports  

---

**⭐ If this helps your learning journey, please star this repository!**

Questions or suggestions? Feel free to open an issue or reach out via LinkedIn.
