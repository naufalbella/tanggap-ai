import os
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

# Load environment variables
load_dotenv()

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
app_args = {"agents_dir": AGENT_DIR, "web": True}

# Create FastAPI app with ADK integration
app: FastAPI = get_fast_api_app(**app_args)
print(f"🔵 Available routes: {[route.path for route in app.routes if not route.path.startswith('/static')]}")

# Update app metadata
app.title = "TanggapAI - Customer Feedback Analyzer"
app.description = "Enterprise Customer Feedback Analyzer and Root Cause Intelligence powered by Gemma"
app.version = "1.0.0"

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "tanggap-ai-agent"}

@app.get("/")
def root():
    return {
        "service": "TanggapAI - Customer Feedback Analyzer",
        "description": "Enterprise Customer Feedback Analyzer and Root Cause Intelligence",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
