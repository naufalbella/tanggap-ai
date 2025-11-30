from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class FeedbackInput(BaseModel):
    """Input model for feedback analysis request"""
    feedback: str = Field(..., min_length=1, max_length=5000, description="Customer feedback text")

class FeedbackAnalysis(BaseModel):
    """Complete feedback analysis with metadata for storage"""
    id: str = Field(..., description="Unique ID")
    feedback_text: str = Field(..., description="Original feedback")
    sentiment: str = Field(..., description="positive, neutral, or negative")
    category: str = Field(..., description="delivery, product, service, payment, technical")
    priority_score: int = Field(..., ge=1, le=5, description="Priority score 1-5")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    root_cause: str = Field(..., description="Root cause analysis")
    recommendation: str = Field(..., description="Improvement recommendation")
    summary: str = Field(..., description="Brief summary")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "feedback_text": "Website slow during peak hours",
                "sentiment": "negative",
                "category": "technical",
                "priority_score": 3,
                "keywords": ["website", "slow", "peak hours"],
                "root_cause": "Server capacity issues",
                "recommendation": "Scale resources",
                "summary": "Performance issues during high traffic.",
                "created_at": "2025-11-30T10:00:00"
            }
        }