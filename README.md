# TanggapAI - Enterprise Customer Feedback Analyzer

Customer Feedback Analyzer & Root Cause Intelligence system powered by:

-   **Google ADK (Agent Development Kit)** - AI Agent framework
-   **Gemma 3 4B** - LLM model via Ollama
-   **MCP (Model Context Protocol)** - BigQuery integration
-   **BigQuery** - Data warehouse for feedback storage

## 🏗 Architecture

```
┌────────────────────────────────────────────────────────┐
│                    User / Client                        │
└───────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│              Backend API (Optional)                     │
│           FastAPI for orchestration                     │
└───────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│                ADK Agent Server                         │
│         (TanggapAgent with MCP Tools)                   │
│                                                          │
│  Agent → Gemma 4B → Analysis                           │
│     ↓                                                   │
│  MCP Toolbox → BigQuery (insert/query)                 │
└────────────────────────────────────────────────────────┘
```

## ✨ Features

### Analysis Capabilities

-   ✅ **Sentiment Analysis**: positive/neutral/negative
-   ✅ **Category Classification**: delivery, product, service, payment, technical
-   ✅ **Priority Scoring**: 1-5 scale for urgency
-   ✅ **Keyword Extraction**: 2-5 main keywords per feedback
-   ✅ **Root Cause Analysis**: Identify underlying issues
-   ✅ **Recommendations**: Actionable improvement suggestions
-   ✅ **Summary**: Concise one-sentence summary

### MCP Integration

-   ✅ **Direct BigQuery Access**: Agent can store/query data autonomously
-   ✅ **Declarative Configuration**: YAML-based MCP setup
-   ✅ **Tool Abstraction**: Reusable MCP tools for database operations

## 📁 Project Structure

```
tanggap-ai/
├── adk-agent/              # ADK Agent with MCP integration
│   ├── tanggap_agent/
│   │   ├── agent.py        # TanggapAgent with McpToolbox
│   │   └── prompts/        # Analysis prompt templates
│   ├── server.py           # FastAPI server
│   ├── Dockerfile
│   └── pyproject.toml
│
├── mcp/                    # MCP Configuration (used by agent)
│   └── mcp_config.yaml     # ✅ MCP resources & tools
│
├── backend/                # Backend API (optional orchestration)
│   ├── app/
│   │   ├── main.py         # FastAPI endpoints
│   │   ├── models.py       # Pydantic models
│   │   └── services/
│   │       └── agent_client.py  # Agent HTTP client
│   ├── Dockerfile
│   └── requirements.txt
│
├── ollama-backend/         # Ollama + Gemma 3 4B
│   └── Dockerfile
│
├── MCP_IMPLEMENTATION.md   # 📖 MCP implementation guide
├── MIGRATION_GUIDE.md      # 📖 Migration guide
├── ENDPOINT_VERIFICATION.md # 📖 Endpoint testing guide
└── deploy-all.sh           # 🚀 Deployment script
```

## 🚀 Quick Start

### 1. Deploy Ollama Backend (Gemma 4B)

```bash
cd ollama-backend
gcloud run deploy ollama-backend \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 16Gi \
  --cpu 4 \
  --gpu 1 \
  --gpu-type nvidia-l4 \
  --set-env-vars MODEL=gemma3:4b
```

### 2. Deploy ADK Agent with MCP

```bash
cd adk-agent

# Set Ollama URL
export OLLAMA_URL=<your-ollama-url>

gcloud run deploy tanggap-adk-agent \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=bnb25-labs \
  --set-env-vars OLLAMA_API_BASE=$OLLAMA_URL \
  --set-env-vars GEMMA_MODEL_NAME=gemma3:4b
```

### 3. Test Agent

```bash
export AGENT_URL=<your-agent-url>

curl -X POST $AGENT_URL/agents/tanggap_agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Website slow during peak hours"
  }'
```

Expected response:

```json
{
    "sentiment": "negative",
    "category": "technical",
    "priority": 3,
    "keywords": ["website", "slow", "peak hours"],
    "root_cause": "Server capacity issues",
    "recommendation": "Scale server resources",
    "summary": "Website performance degrades during high traffic."
}
```

## 🔧 MCP Integration Details

### Configuration (`mcp/mcp_config.yaml`)

```yaml
mcpServers:
    bigquery:
        command: python
        args: ["-m", "google.adk.toolboxes.bigquery_mcp_server"]
        env:
            GOOGLE_CLOUD_PROJECT: bnb25-labs
            BIGQUERY_DATASET: tanggapai_dataset
            BIGQUERY_TABLE: feedback_analysis

tools:
    - name: insert_feedback
      description: "Insert analyzed feedback into BigQuery"
    - name: query_feedback
      description: "Query feedback data from BigQuery"
```

### Agent Implementation

```python
from google.adk.toolboxes.mcp import McpToolbox

mcp_toolbox = McpToolbox(config_path="mcp/mcp_config.yaml")

tanggap_agent = Agent(
    model=LiteLlm(...),
    tools=[mcp_toolbox],  # ✅ MCP integrated
    instruction=TANGGAP_INSTRUCTION
)
```

### How Agent Uses MCP

1. **Auto-store analysis**: Agent can automatically call `insert_feedback` after analysis
2. **Query previous data**: Agent can use `query_feedback` to retrieve historical data
3. **Autonomous operation**: No need for backend to manage BigQuery

See [MCP_IMPLEMENTATION.md](./MCP_IMPLEMENTATION.md) for complete details.

## 📊 BigQuery Schema

```sql
CREATE TABLE tanggapai_dataset.feedback_analysis (
  id STRING,
  feedback_text STRING,
  sentiment STRING,
  category STRING,
  priority_score INTEGER,
  keywords ARRAY<STRING>,
  root_cause STRING,
  recommendation STRING,
  summary STRING,
  created_at TIMESTAMP
)
```

## 🧪 Testing

### Local Development

```bash
# Install dependencies
cd adk-agent
uv sync

# Run agent server
python server.py

# Access Web UI
open http://localhost:8080
```

### Test with MCP Tools

```bash
# Analysis with auto-store
curl -X POST http://localhost:8080/agents/tanggap_agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Product quality excellent. Store in BigQuery."
  }'

# Query previous feedback
curl -X POST http://localhost:8080/agents/tanggap_agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Show last 5 negative feedbacks from database"
  }'
```

## 📈 Model Evolution

| Version | Model       | Issue                                              | Solution      |
| ------- | ----------- | -------------------------------------------------- | ------------- |
| v1      | gemma3:270m | Hallucination, returns example instead of analysis | Too small     |
| v2      | gemma2:2b   | Better but inconsistent JSON                       | Still limited |
| v3      | gemma3:4b   | ✅ Reliable instruction following                  | **Current**   |

## 🔐 Environment Variables

### ADK Agent

```bash
GOOGLE_CLOUD_PROJECT=bnb25-labs
GOOGLE_CLOUD_LOCATION=europe-west1
GEMMA_MODEL_NAME=gemma3:4b
OLLAMA_API_BASE=<ollama-backend-url>
```

### Ollama Backend

```bash
MODEL=gemma3:4b
OLLAMA_NUM_GPU=999
```

## 📖 Documentation

-   [MCP Implementation Guide](./MCP_IMPLEMENTATION.md) - Complete MCP architecture & implementation
-   [ADK Agent README](./adk-agent/README.md) - Agent-specific documentation
-   [Backend README](./backend/README.md) - Backend API documentation

## 🎯 Use Cases

### 1. Autonomous Analysis + Storage

Agent analyzes feedback and automatically stores in BigQuery via MCP.

### 2. Historical Analysis

Agent queries previous feedback to provide context-aware recommendations.

### 3. Batch Processing

Process multiple feedbacks with agent storing each to BigQuery.

### 4. Real-time Dashboard

Query BigQuery directly for real-time analytics dashboard.

## 🏆 Advantages

### MCP Integration Benefits

-   **Agent Autonomy**: Direct database access without backend
-   **Declarative Config**: YAML-based tool definition
-   **Reusability**: MCP tools usable across agents
-   **Separation of Concerns**: Clean architecture

### vs Direct BigQuery

| Aspect            | Direct | MCP  |
| ----------------- | ------ | ---- |
| Agent Access      | ❌     | ✅   |
| Tool Abstraction  | ❌     | ✅   |
| Config Management | Code   | YAML |
| Reusability       | Low    | High |

## 📝 License

MIT

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

---

**Built with Google ADK + MCP + Gemma 3 4B**
