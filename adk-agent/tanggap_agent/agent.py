import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
import google.auth

# Load environment variables
root_dir = Path(__file__).parent.parent
dotenv_path = root_dir / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Configure Google Cloud
try:
    _, project_id = google.auth.default()
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
except Exception:
    pass

os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "europe-west1")



# Configure model connection - Using larger model for better instruction following
gemma_model_name = os.getenv("GEMMA_MODEL_NAME", "gemma3:4b")
api_base = os.getenv("OLLAMA_API_BASE", "localhost:10010")  # Location of Ollama server

# TanggapAgent - Customer Feedback Analyzer & Root Cause Intelligence
TANGGAP_INSTRUCTION = """You are TanggapAgent - an AI that analyzes customer feedback.

YOUR TASK:
When you receive feedback text, analyze it and return ONLY a JSON object (no markdown, no explanations) with these fields:

{
  "sentiment": "positive" | "neutral" | "negative",
  "category": "delivery" | "product" | "service" | "payment" | "technical",
  "priority": 1-5 (integer: 1=low, 5=critical),
  "keywords": ["keyword1", "keyword2", ...],
  "root_cause": "explanation of what caused this issue",
  "recommendation": "actionable solution to address the issue",
  "summary": "one-sentence description of the feedback"
}

IMPORTANT:
- Return ONLY the JSON object, nothing else
- No markdown code blocks (no ```json)
- No additional text or explanations
- All fields are required

EXAMPLES:

Feedback: "Delivery saya telat 3 hari"
{
  "sentiment": "negative",
  "category": "delivery",
  "priority": 4,
  "keywords": ["delivery", "late", "3 days"],
  "root_cause": "Shipping delay",
  "recommendation": "Improve logistics tracking",
  "summary": "Delivery delayed by 3 days."
}

Feedback: "Website slow during peak hours"
{
  "sentiment": "negative",
  "category": "technical",
  "priority": 3,
  "keywords": ["website", "slow", "peak hours"],
  "root_cause": "Server capacity issues",
  "recommendation": "Scale server resources",
  "summary": "Website performance degrades during high traffic."
}

Feedback: "Product quality is excellent"
{
  "sentiment": "positive",
  "category": "product",
  "priority": 1,
  "keywords": ["product", "quality", "excellent"],
  "root_cause": "Good manufacturing standards",
  "recommendation": "Maintain current quality",
  "summary": "Customer satisfied with product quality."
}

Now analyze this feedback:"""



# TanggapAgent - Production Feedback Analysis Agent
tanggap_agent = Agent(
    model=LiteLlm(
        model=f"ollama_chat/{gemma_model_name}",
        api_base=api_base
    ),
    name="tanggap_agent",
    description="TanggapAgent - Enterprise Customer Feedback Analyzer and Root Cause Intelligence system.",
    instruction=TANGGAP_INSTRUCTION,
    tools=[],  # No tools - just return JSON analysis
)

# Set as root agent
root_agent = tanggap_agent