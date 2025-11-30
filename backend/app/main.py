"""TanggapAI Backend API

Simplified backend that delegates to ADK Agent.
Agent autonomously handles analysis + BigQuery storage via tool functions.
"""
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import FeedbackInput, FeedbackAnalysis
from app.services.agent_client import analyze_feedback

# Create FastAPI app
app = FastAPI(
    title="TanggapAI API",
    description="Customer Feedback Analyzer and Root Cause Intelligence API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "TanggapAI Backend API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "POST /api/analyze",
            "query": "GET /api/query",
            "health": "GET /health"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "tanggap-ai-backend"}

@app.post("/api/analyze", response_model=FeedbackAnalysis)
async def analyze_feedback_endpoint(input_data: FeedbackInput):
    """
    Analyze customer feedback and store to BigQuery
    
    Flow:
    1. Receive feedback text
    2. Generate ID and timestamp
    3. Call ADK Agent for analysis (returns JSON only)
    4. Backend stores result to BigQuery
    5. Return analysis
    
    Example Input:
    {
        "feedback": "The website is very slow during peak hours"
    }
    
    Example Output:
    {
        "id": "uuid",
        "feedback_text": "The website is very slow during peak hours",
        "sentiment": "negative",
        "category": "technical",
        "priority_score": 3,
        "keywords": ["website", "slow", "peak hours"],
        "root_cause": "Server capacity issues",
        "recommendation": "Scale server resources",
        "summary": "Website performance degrades during high traffic.",
        "created_at": "2025-11-30T10:00:00Z"
    }
    
    """
    try:
        from app.services.bq_client import insert_feedback_analysis
        
        # Generate unique ID and timestamp
        analysis_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        created_at_iso = created_at.isoformat() + "Z"
        
        # Call ADK Agent for analysis (returns JSON only, no tools)
        analysis = await analyze_feedback(
            feedback_text=input_data.feedback,
            record_id=analysis_id,
            created_at=created_at_iso
        )
        
        # Backend stores to BigQuery
        bq_result = insert_feedback_analysis(
            record_id=analysis_id,
            feedback_text=input_data.feedback,
            sentiment=analysis["sentiment"],
            category=analysis["category"],
            priority=analysis["priority"],
            keywords=analysis["keywords"],
            root_cause=analysis["root_cause"],
            recommendation=analysis["recommendation"],
            summary=analysis["summary"],
            created_at=created_at_iso
        )
        
        if not bq_result.get("success"):
            print(f"⚠️ BigQuery insert failed: {bq_result.get('error')}")
        
        # Create full analysis object for response
        feedback_analysis = FeedbackAnalysis(
            id=analysis_id,
            feedback_text=input_data.feedback,
            sentiment=analysis["sentiment"],
            category=analysis["category"],
            priority_score=analysis["priority"],
            keywords=analysis["keywords"],
            root_cause=analysis["root_cause"],
            recommendation=analysis["recommendation"],
            summary=analysis["summary"],
            created_at=created_at
        )
        
        return feedback_analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/query")
async def query_feedbacks(limit: int = 10, sentiment: str = None, category: str = None):
    """
    Query feedback analysis from BigQuery
    
    Parameters:
    - limit: Number of records to return (default: 10, max: 100)
    - sentiment: Filter by sentiment (positive, neutral, negative)
    - category: Filter by category (delivery, product, service, payment, technical)
    
    Examples:
    - GET /api/query?limit=5
    - GET /api/query?sentiment=negative&limit=20
    - GET /api/query?category=technical
    """
    try:
        from app.services.bq_client import query_feedback
        
        # Build filters
        filters = {}
        if sentiment:
            filters["sentiment"] = sentiment
        if category:
            filters["category"] = category
        
        # Query BigQuery
        result = query_feedback(limit=min(limit, 100), filters=filters)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
