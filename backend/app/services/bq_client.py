"""BigQuery client for storing and querying feedback analysis"""
import os
from typing import Dict, List
from google.cloud import bigquery
from datetime import datetime

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "bnb25-labs")
DATASET_ID = "tanggapai_dataset"
TABLE_ID = "feedback_analysis"
FULL_TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

# Initialize BigQuery client
bq_client = bigquery.Client(project=PROJECT_ID)


def insert_feedback_analysis(
    record_id: str,
    feedback_text: str,
    sentiment: str,
    category: str,
    priority: int,
    keywords: List[str],
    root_cause: str,
    recommendation: str,
    summary: str,
    created_at: str
) -> Dict:
    """Insert feedback analysis into BigQuery"""
    try:
        row = {
            "id": record_id,
            "feedback_text": feedback_text,
            "sentiment": sentiment,
            "category": category,
            "priority_score": priority,  # Note: table uses priority_score
            "keywords": keywords,
            "root_cause": root_cause,
            "recommendation": recommendation,
            "summary": summary,
            "created_at": created_at,
        }
        
        print(f"🔵 Inserting feedback to BigQuery: {record_id}")
        errors = bq_client.insert_rows_json(FULL_TABLE_ID, [row])
        
        if errors:
            print(f"❌ BigQuery insert errors: {errors}")
            return {"success": False, "error": str(errors)}
        
        print(f"✅ Successfully inserted record {record_id} to BigQuery")
        return {"success": True, "message": f"Inserted record {record_id}"}
    except Exception as e:
        print(f"❌ Exception inserting to BigQuery: {e}")
        return {"success": False, "error": str(e)}


def query_feedback(limit: int = 100, filters: Dict = None) -> Dict:
    """Query feedback from BigQuery with optional filters"""
    try:
        # Build WHERE clause from filters
        where_clauses = []
        if filters:
            if "sentiment" in filters:
                where_clauses.append(f"sentiment = '{filters['sentiment']}'")
            if "category" in filters:
                where_clauses.append(f"category = '{filters['category']}'")
        
        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)
        
        query = f"""
            SELECT *
            FROM `{FULL_TABLE_ID}`
            {where_sql}
            ORDER BY created_at DESC
            LIMIT {limit}
        """
        
        print(f"🔵 Querying BigQuery with: {query}")
        query_job = bq_client.query(query)
        results = query_job.result()
        
        data = [dict(row) for row in results]
        
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        print(f"❌ Exception querying BigQuery: {e}")
        return {"success": False, "error": str(e)}
