"""Client for calling ADK Agent API"""
import os
import httpx
import json
import re
from typing import Dict

AGENT_URL = os.getenv("AGENT_URL", "https://tanggap-ai-adk-agent-gatfv4h2ua-ew.a.run.app")
AGENT_TIMEOUT = 60  # seconds

def extract_json_from_text(text: str) -> Dict:
    """Extract JSON from response text that might have markdown formatting"""
    # Try to find JSON in code blocks
    json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to find raw JSON
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    
    raise ValueError(f"Could not extract valid JSON from response: {text[:200]}")

async def analyze_feedback(feedback_text: str, record_id: str, created_at: str) -> Dict:
    """
    Call ADK Agent to analyze feedback and return JSON analysis
    
    Args:
        feedback_text: Customer feedback to analyze
        record_id: Unique ID for the feedback record (not used by agent, kept for API compatibility)
        created_at: ISO 8601 timestamp (not used by agent, kept for API compatibility)
        
    Returns:
        Dict with analysis: sentiment, category, priority, keywords, root_cause, recommendation, summary
    """
    async with httpx.AsyncClient(timeout=AGENT_TIMEOUT) as client:
        try:
            # Prepare simple prompt for analysis
            prompt = f"Analyze this feedback: {feedback_text}"
            
            # First, create a session
            session_response = await client.post(
                f"{AGENT_URL}/apps/tanggap_agent/users/default_user/sessions",
                json={}
            )
            session_response.raise_for_status()
            session_data = session_response.json()
            session_id = session_data.get("id") or session_data.get("session_id") or record_id
            
            # Now call ADK Agent API using /run_sse endpoint
            async with client.stream(
                "POST",
                f"{AGENT_URL}/run_sse",
                json={
                    "app_name": "tanggap_agent",
                    "user_id": "default_user",
                    "session_id": session_id,
                    "newMessage": {
                        "role": "user",
                        "parts": [{"text": prompt}]
                    },
                    "model_config": {}
                }
            ) as response:
                response.raise_for_status()
                
                # Collect SSE events
                full_response = ""
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix
                        if data_str and data_str != "[DONE]":
                            try:
                                event_data = json.loads(data_str)
                                # Accumulate response content
                                if "content" in event_data:
                                    content_val = event_data["content"]
                                    if isinstance(content_val, str):
                                        full_response += content_val
                                    elif isinstance(content_val, dict):
                                        full_response += json.dumps(content_val)
                                elif "message" in event_data and "parts" in event_data["message"]:
                                    for part in event_data["message"]["parts"]:
                                        if "text" in part:
                                            text_val = part["text"]
                                            if isinstance(text_val, str):
                                                full_response += text_val
                                            elif isinstance(text_val, dict):
                                                full_response += json.dumps(text_val)
                            except json.JSONDecodeError:
                                continue
            
            # Use accumulated response as content
            content = full_response if full_response else ""
            
            if not content:
                raise ValueError("No content received from agent")
            
            # Parse the accumulated content as JSON
            # Agent returns SSE format with parts array
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                raise ValueError(f"Could not parse JSON from agent response: {content[:200]}")
            
            print(f"🔵 Parsed structure: {parsed.keys() if isinstance(parsed, dict) else type(parsed)}")
            
            # Extract text from parts array if present
            analysis_text = None
            if "parts" in parsed and isinstance(parsed["parts"], list):
                for part in parsed["parts"]:
                    if "text" in part:
                        analysis_text = part["text"]
                        break
            
            if not analysis_text:
                raise ValueError(f"No text found in parts. Response: {parsed}")
            
            print(f"🔵 Analysis text: {analysis_text[:200]}")
            
            # Parse the analysis text as JSON
            try:
                analysis = json.loads(analysis_text)
            except json.JSONDecodeError:
                # Try extracting JSON from markdown
                analysis = extract_json_from_text(analysis_text)
            
            # Validate required fields
            required_fields = ["sentiment", "category", "priority", "keywords", "root_cause", "recommendation", "summary"]
            missing = [f for f in required_fields if f not in analysis]
            
            if missing:
                raise ValueError(f"Missing required fields: {missing}. Got fields: {list(analysis.keys())}")
            
            return analysis
            
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
            raise Exception(f"Failed to call ADK Agent: {e} - Response: {error_detail}")
        except httpx.HTTPError as e:
            raise Exception(f"Failed to call ADK Agent: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse agent response: {e}")
        except Exception as e:
            raise Exception(f"Error analyzing feedback: {e}")