# TanggapAI - Enterprise Customer Feedback Analyzer

AI-powered customer feedback analyzer that identifies sentiment, categorizes issues, and provides root cause analysis with actionable recommendations.

## 🎯 Overview

TanggapAI is an intelligent system that analyzes customer feedback using:

-   **Google ADK (Agent Development Kit)** - AI Agent framework
-   **Gemma 3 4B** - Large Language Model via Ollama
-   **FastAPI** - Backend API and agent server
-   **BigQuery** - Data warehouse for feedback storage and analytics

## 🏗 Architecture

```
┌────────────────────────────────────────────────────────┐
│                    User / Client                        │
└───────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│              Backend API (FastAPI)                      │
│   - Receives feedback                                   │
│   - Generates IDs & timestamps                          │
│   - Stores results to BigQuery                          │
└───────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│           ADK Agent Server (FastAPI)                    │
│                                                          │
│  TanggapAgent → Gemma 4B → JSON Analysis               │
│                                                          │
│  Returns: sentiment, category, priority,               │
│           keywords, root_cause, recommendation          │
└────────────┬───────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────┐
│              Ollama Backend                             │
│           Gemma 3 4B Model Server                       │
└────────────────────────────────────────────────────────┘
```

## ✨ Features

### 🎯 Analysis Capabilities

-   ✅ **Sentiment Analysis**: Classifies feedback as positive, neutral, or negative
-   ✅ **Category Classification**: Categorizes into delivery, product, service, payment, or technical
-   ✅ **Priority Scoring**: Assigns urgency score from 1 (low) to 5 (critical)
-   ✅ **Keyword Extraction**: Identifies 2-5 key terms from each feedback
-   ✅ **Root Cause Analysis**: Determines underlying issues causing the feedback
-   ✅ **Actionable Recommendations**: Provides specific solutions to address problems
-   ✅ **Summary Generation**: Creates concise one-sentence feedback summaries

### 🔧 Technical Features

-   ✅ **RESTful API**: Easy integration with existing systems
-   ✅ **BigQuery Storage**: Scalable data warehouse for analytics
-   ✅ **Cloud-Ready**: Designed for Google Cloud Run deployment
-   ✅ **Production-Grade**: Error handling, logging, and health checks
-   ✅ **CORS Support**: Ready for web frontend integration

## 📁 Project Structure

```
tanggap-ai/
├── adk-agent/              # ADK Agent Server
│   ├── tanggap_agent/
│   │   ├── __init__.py
│   │   └── agent.py        # TanggapAgent with Gemma 4B
│   ├── server.py           # FastAPI server for agent
│   ├── Dockerfile          # Container for agent server
│   └── pyproject.toml      # Dependencies (google-adk, litellm, etc.)
│
├── backend/                # Backend API
│   ├── app/
│   │   ├── main.py         # FastAPI endpoints (/api/analyze, /api/query)
│   │   ├── models.py       # Pydantic models (FeedbackInput, FeedbackAnalysis)
│   │   └── services/
│   │       ├── agent_client.py   # HTTP client for ADK Agent
│   │       └── bq_client.py      # BigQuery operations
│   ├── deploy.sh           # Deployment script
│   ├── Dockerfile          # Container for backend
│   └── requirements.txt    # Dependencies (fastapi, httpx, google-cloud-bigquery)
│
├── ollama-backend/         # Ollama Server
│   └── Dockerfile          # Gemma 3 4B model server
│
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

-   Google Cloud Project with billing enabled
-   `gcloud` CLI installed and configured
-   BigQuery dataset and table created (see [BigQuery Setup](#-bigquery-setup))

### 1. Deploy Ollama Backend (Gemma 3 4B)

Deploy the Ollama server with Gemma 3 4B model:

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

### 2. Deploy ADK Agent Server

Deploy the agent server that performs the analysis:

```bash
cd adk-agent

# Get Ollama URL from step 1
export OLLAMA_URL=$(gcloud run services describe ollama-backend \
  --region=europe-west1 --format='value(status.url)')

gcloud run deploy tanggap-ai-adk-agent \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project) \
  --set-env-vars OLLAMA_API_BASE=$OLLAMA_URL \
  --set-env-vars GEMMA_MODEL_NAME=gemma3:4b
```

### 3. Deploy Backend API

Deploy the backend API that orchestrates the system:

```bash
cd backend
./deploy.sh
```

This script automatically:

-   Retrieves the ADK Agent URL
-   Deploys the backend with proper configuration
-   Connects to BigQuery for data storage

### 4. Test the System

Get your backend URL:

```bash
export BACKEND_URL=$(gcloud run services describe tanggap-ai-backend \
  --region=europe-west1 --format='value(status.url)')
```

Analyze feedback:

```bash
curl -X POST $BACKEND_URL/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": "Website slow during peak hours"
  }'
```

Expected response:

```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "feedback_text": "Website slow during peak hours",
    "sentiment": "negative",
    "category": "technical",
    "priority_score": 3,
    "keywords": ["website", "slow", "peak hours"],
    "root_cause": "Server capacity issues",
    "recommendation": "Scale server resources",
    "summary": "Website performance degrades during high traffic.",
    "created_at": "2025-11-30T10:00:00Z"
}
```

Query stored feedback:

```bash
# Get last 10 feedbacks
curl $BACKEND_URL/api/query?limit=10

# Filter by sentiment
curl $BACKEND_URL/api/query?sentiment=negative&limit=5

# Filter by category
curl $BACKEND_URL/api/query?category=technical
```

## 🔧 API Endpoints

### Backend API (`/api/*`)

#### POST `/api/analyze`

Analyze customer feedback and store results.

**Request:**

```json
{
    "feedback": "The website is very slow during peak hours"
}
```

**Response:**

```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
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
```

#### GET `/api/query`

Query feedback data from BigQuery.

**Parameters:**

-   `limit` (int, optional): Number of records to return (default: 10, max: 100)
-   `sentiment` (string, optional): Filter by sentiment (positive, neutral, negative)
-   `category` (string, optional): Filter by category (delivery, product, service, payment, technical)

**Examples:**

```bash
# Get last 10 feedbacks
GET /api/query?limit=10

# Filter by sentiment
GET /api/query?sentiment=negative&limit=20

# Filter by category
GET /api/query?category=technical
```

### ADK Agent API (`/agents/*`)

#### POST `/agents/tanggap_agent/run`

Direct access to the agent (used internally by backend).

**Request:**

```json
{
    "user_input": "Website slow during peak hours"
}
```

**Response:**

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

## 📊 BigQuery Setup

### Create Dataset and Table

```sql
-- Create dataset
CREATE SCHEMA IF NOT EXISTS `tanggapai_dataset`
OPTIONS(
  location="europe-west1",
  description="TanggapAI feedback analysis dataset"
);

-- Create table
CREATE TABLE IF NOT EXISTS `tanggapai_dataset.feedback_analysis` (
  id STRING NOT NULL,
  feedback_text STRING NOT NULL,
  sentiment STRING NOT NULL,
  category STRING NOT NULL,
  priority_score INT64 NOT NULL,
  keywords ARRAY<STRING>,
  root_cause STRING,
  recommendation STRING,
  summary STRING,
  created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
OPTIONS(
  description="Customer feedback analysis results"
);
```

### Field Descriptions

| Field            | Type            | Description                                    |
| ---------------- | --------------- | ---------------------------------------------- |
| `id`             | STRING          | Unique identifier (UUID)                       |
| `feedback_text`  | STRING          | Original customer feedback                     |
| `sentiment`      | STRING          | positive, neutral, or negative                 |
| `category`       | STRING          | delivery, product, service, payment, technical |
| `priority_score` | INT64           | Urgency score (1=low, 5=critical)              |
| `keywords`       | ARRAY\<STRING\> | Key terms extracted from feedback              |
| `root_cause`     | STRING          | Identified underlying issue                    |
| `recommendation` | STRING          | Actionable solution                            |
| `summary`        | STRING          | One-sentence summary                           |
| `created_at`     | TIMESTAMP       | Analysis timestamp                             |

## 🧪 Local Development

### Setup Agent Server

```bash
cd adk-agent

# Create .env file
cat > .env << EOF
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=europe-west1
GEMMA_MODEL_NAME=gemma3:4b
OLLAMA_API_BASE=http://localhost:11434
EOF

# Install dependencies (using uv)
uv sync

# Run agent server
python server.py

# Access Web UI
open http://localhost:8080
```

### Setup Backend API

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_CLOUD_PROJECT=your-project-id
export AGENT_URL=http://localhost:8080

# Run backend
python -m app.main

# Access API
open http://localhost:8080/docs
```

### Testing

```bash
# Test agent directly
curl -X POST http://localhost:8080/agents/tanggap_agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Product quality excellent"
  }'

# Test backend API
curl -X POST http://localhost:8080/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": "Delivery was 3 days late"
  }'

# Query data
curl "http://localhost:8080/api/query?limit=5"
```

## 🔐 Environment Variables

### ADK Agent (`adk-agent/.env`)

| Variable                | Description             | Example                   |
| ----------------------- | ----------------------- | ------------------------- |
| `GOOGLE_CLOUD_PROJECT`  | Google Cloud project ID | `your-project-id`         |
| `GOOGLE_CLOUD_LOCATION` | GCP region              | `europe-west1`            |
| `GEMMA_MODEL_NAME`      | Gemma model version     | `gemma3:4b`               |
| `OLLAMA_API_BASE`       | Ollama server URL       | `http://ollama-url:11434` |

### Backend API (`backend/.env`)

| Variable               | Description             | Example                 |
| ---------------------- | ----------------------- | ----------------------- |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID | `your-project-id`       |
| `AGENT_URL`            | ADK Agent server URL    | `http://agent-url:8080` |

### Ollama Backend

| Variable         | Description                    | Example     |
| ---------------- | ------------------------------ | ----------- |
| `MODEL`          | Model to load                  | `gemma3:4b` |
| `OLLAMA_NUM_GPU` | Number of GPUs (999 = use all) | `999`       |

## 📈 Model Selection

The project uses **Gemma 3 4B** for optimal balance between performance and accuracy:

| Model         | Size   | Performance | Issues                   | Status         |
| ------------- | ------ | ----------- | ------------------------ | -------------- |
| gemma3:270m   | 270M   | Fast        | Hallucinations, examples | ❌ Rejected    |
| gemma2:2b     | 2B     | Moderate    | Inconsistent JSON format | ❌ Rejected    |
| **gemma3:4b** | **4B** | **Good**    | **None**                 | ✅ **Current** |

**Why Gemma 3 4B?**

-   Reliable instruction following
-   Consistent JSON output format
-   Accurate sentiment and category classification
-   Good root cause analysis quality
-   Reasonable resource requirements (16GB GPU memory)

## 🎯 Use Cases

### 1. Customer Support Analytics

Analyze incoming support tickets to:

-   Identify trending issues
-   Prioritize critical problems
-   Track sentiment over time
-   Generate actionable insights

### 2. Product Feedback Management

Process user feedback to:

-   Categorize feature requests
-   Identify product quality issues
-   Track customer satisfaction
-   Guide product roadmap decisions

### 3. Service Quality Monitoring

Monitor service feedback to:

-   Detect delivery problems
-   Identify technical issues
-   Measure service quality
-   Improve operational processes

### 4. Real-Time Dashboard

Build analytics dashboards by:

-   Querying BigQuery directly
-   Visualizing sentiment trends
-   Tracking category distribution
-   Monitoring priority scores

## 🏆 Key Benefits

### For Developers

-   **Clean Architecture**: Separation between agent logic and API orchestration
-   **Easy Integration**: RESTful API with clear endpoints
-   **Cloud-Native**: Designed for Google Cloud Run
-   **Scalable**: Handles concurrent requests efficiently

### For Business

-   **Automated Analysis**: Save hours of manual feedback review
-   **Actionable Insights**: Get specific recommendations, not just classifications
-   **Data-Driven Decisions**: Historical data in BigQuery for trend analysis
-   **Cost-Effective**: Serverless architecture scales to zero when not in use

## 🔍 Example Analyses

### Example 1: Technical Issue

**Input:**

```json
{
    "feedback": "Website slow during peak hours"
}
```

**Output:**

```json
{
    "sentiment": "negative",
    "category": "technical",
    "priority_score": 3,
    "keywords": ["website", "slow", "peak hours"],
    "root_cause": "Server capacity issues",
    "recommendation": "Scale server resources",
    "summary": "Website performance degrades during high traffic."
}
```

### Example 2: Delivery Problem

**Input:**

```json
{
    "feedback": "Delivery saya telat 3 hari"
}
```

**Output:**

```json
{
    "sentiment": "negative",
    "category": "delivery",
    "priority_score": 4,
    "keywords": ["delivery", "late", "3 days"],
    "root_cause": "Shipping delay",
    "recommendation": "Improve logistics tracking",
    "summary": "Delivery delayed by 3 days."
}
```

### Example 3: Positive Feedback

**Input:**

```json
{
    "feedback": "Product quality is excellent"
}
```

**Output:**

```json
{
    "sentiment": "positive",
    "category": "product",
    "priority_score": 1,
    "keywords": ["product", "quality", "excellent"],
    "root_cause": "Good manufacturing standards",
    "recommendation": "Maintain current quality",
    "summary": "Customer satisfied with product quality."
}
```

## 🛠️ Technology Stack

| Component           | Technology       | Purpose                        |
| ------------------- | ---------------- | ------------------------------ |
| **Agent Framework** | Google ADK       | AI agent orchestration         |
| **LLM Model**       | Gemma 3 4B       | Natural language understanding |
| **Model Server**    | Ollama           | LLM inference                  |
| **Backend API**     | FastAPI          | REST API endpoints             |
| **Data Storage**    | BigQuery         | Scalable data warehouse        |
| **Deployment**      | Google Cloud Run | Serverless container platform  |
| **Language**        | Python 3.11+     | Core programming language      |
| **HTTP Client**     | httpx            | Async HTTP requests            |

## 📝 License

MIT

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using Google ADK + Gemma 3 4B + BigQuery**
# TanggapAI - Enterprise Customer Feedback Analyzer

AI-powered customer feedback analyzer that identifies sentiment, categorizes issues, and provides root cause analysis with actionable recommendations.

## 🎯 Overview

TanggapAI is an intelligent system that analyzes customer feedback using:

-   **Google ADK (Agent Development Kit)** - AI Agent framework
-   **Gemma 3 4B** - Large Language Model via Ollama
-   **FastAPI** - Backend API and agent server
-   **BigQuery** - Data warehouse for feedback storage and analytics

## 🏗 Architecture

```
┌────────────────────────────────────────────────────────┐
│                    User / Client                        │
└───────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│              Backend API (FastAPI)                      │
│   - Receives feedback                                   │
│   - Generates IDs & timestamps                          │
│   - Stores results to BigQuery                          │
└───────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│           ADK Agent Server (FastAPI)                    │
│                                                          │
│  TanggapAgent → Gemma 4B → JSON Analysis               │
│                                                          │
│  Returns: sentiment, category, priority,               │
│           keywords, root_cause, recommendation          │
└────────────┬───────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────┐
│              Ollama Backend                             │
│           Gemma 3 4B Model Server                       │
└────────────────────────────────────────────────────────┘
```

## ✨ Features

### 🎯 Analysis Capabilities

-   ✅ **Sentiment Analysis**: Classifies feedback as positive, neutral, or negative
-   ✅ **Category Classification**: Categorizes into delivery, product, service, payment, or technical
-   ✅ **Priority Scoring**: Assigns urgency score from 1 (low) to 5 (critical)
-   ✅ **Keyword Extraction**: Identifies 2-5 key terms from each feedback
-   ✅ **Root Cause Analysis**: Determines underlying issues causing the feedback
-   ✅ **Actionable Recommendations**: Provides specific solutions to address problems
-   ✅ **Summary Generation**: Creates concise one-sentence feedback summaries

### 🔧 Technical Features

-   ✅ **RESTful API**: Easy integration with existing systems
-   ✅ **BigQuery Storage**: Scalable data warehouse for analytics
-   ✅ **Cloud-Ready**: Designed for Google Cloud Run deployment
-   ✅ **Production-Grade**: Error handling, logging, and health checks
-   ✅ **CORS Support**: Ready for web frontend integration

## 📁 Project Structure

```
tanggap-ai/
├── adk-agent/              # ADK Agent Server
│   ├── tanggap_agent/
│   │   ├── __init__.py
│   │   └── agent.py        # TanggapAgent with Gemma 4B
│   ├── server.py           # FastAPI server for agent
│   ├── Dockerfile          # Container for agent server
│   └── pyproject.toml      # Dependencies (google-adk, litellm, etc.)
│
├── backend/                # Backend API
│   ├── app/
│   │   ├── main.py         # FastAPI endpoints (/api/analyze, /api/query)
│   │   ├── models.py       # Pydantic models (FeedbackInput, FeedbackAnalysis)
│   │   └── services/
│   │       ├── agent_client.py   # HTTP client for ADK Agent
│   │       └── bq_client.py      # BigQuery operations
│   ├── deploy.sh           # Deployment script
│   ├── Dockerfile          # Container for backend
│   └── requirements.txt    # Dependencies (fastapi, httpx, google-cloud-bigquery)
│
├── ollama-backend/         # Ollama Server
│   └── Dockerfile          # Gemma 3 4B model server
│
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

-   Google Cloud Project with billing enabled
-   `gcloud` CLI installed and configured
-   BigQuery dataset and table created (see [BigQuery Setup](#-bigquery-setup))

### 1. Deploy Ollama Backend (Gemma 3 4B)

Deploy the Ollama server with Gemma 3 4B model:

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

### 2. Deploy ADK Agent Server

Deploy the agent server that performs the analysis:

```bash
cd adk-agent

# Get Ollama URL from step 1
export OLLAMA_URL=$(gcloud run services describe ollama-backend \
  --region=europe-west1 --format='value(status.url)')

gcloud run deploy tanggap-ai-adk-agent \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project) \
  --set-env-vars OLLAMA_API_BASE=$OLLAMA_URL \
  --set-env-vars GEMMA_MODEL_NAME=gemma3:4b
```

### 3. Deploy Backend API

Deploy the backend API that orchestrates the system:

```bash
cd backend
./deploy.sh
```

This script automatically:

-   Retrieves the ADK Agent URL
-   Deploys the backend with proper configuration
-   Connects to BigQuery for data storage

### 4. Test the System

Get your backend URL:

```bash
export BACKEND_URL=$(gcloud run services describe tanggap-ai-backend \
  --region=europe-west1 --format='value(status.url)')
```

Analyze feedback:

```bash
curl -X POST $BACKEND_URL/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": "Website slow during peak hours"
  }'
```

Expected response:

```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "feedback_text": "Website slow during peak hours",
    "sentiment": "negative",
    "category": "technical",
    "priority_score": 3,
    "keywords": ["website", "slow", "peak hours"],
    "root_cause": "Server capacity issues",
    "recommendation": "Scale server resources",
    "summary": "Website performance degrades during high traffic.",
    "created_at": "2025-11-30T10:00:00Z"
}
```

Query stored feedback:

```bash
# Get last 10 feedbacks
curl $BACKEND_URL/api/query?limit=10

# Filter by sentiment
curl $BACKEND_URL/api/query?sentiment=negative&limit=5

# Filter by category
curl $BACKEND_URL/api/query?category=technical
```

## 🔧 API Endpoints

### Backend API (`/api/*`)

#### POST `/api/analyze`

Analyze customer feedback and store results.

**Request:**

```json
{
    "feedback": "The website is very slow during peak hours"
}
```

**Response:**

```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
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
```

#### GET `/api/query`

Query feedback data from BigQuery.

**Parameters:**

-   `limit` (int, optional): Number of records to return (default: 10, max: 100)
-   `sentiment` (string, optional): Filter by sentiment (positive, neutral, negative)
-   `category` (string, optional): Filter by category (delivery, product, service, payment, technical)

**Examples:**

```bash
# Get last 10 feedbacks
GET /api/query?limit=10

# Filter by sentiment
GET /api/query?sentiment=negative&limit=20

# Filter by category
GET /api/query?category=technical
```

### ADK Agent API (`/agents/*`)

#### POST `/agents/tanggap_agent/run`

Direct access to the agent (used internally by backend).

**Request:**

```json
{
    "user_input": "Website slow during peak hours"
}
```

**Response:**

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

## 📊 BigQuery Setup

### Create Dataset and Table

```sql
-- Create dataset
CREATE SCHEMA IF NOT EXISTS `tanggapai_dataset`
OPTIONS(
  location="europe-west1",
  description="TanggapAI feedback analysis dataset"
);

-- Create table
CREATE TABLE IF NOT EXISTS `tanggapai_dataset.feedback_analysis` (
  id STRING NOT NULL,
  feedback_text STRING NOT NULL,
  sentiment STRING NOT NULL,
  category STRING NOT NULL,
  priority_score INT64 NOT NULL,
  keywords ARRAY<STRING>,
  root_cause STRING,
  recommendation STRING,
  summary STRING,
  created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
OPTIONS(
  description="Customer feedback analysis results"
);
```

### Field Descriptions

| Field            | Type            | Description                                    |
| ---------------- | --------------- | ---------------------------------------------- |
| `id`             | STRING          | Unique identifier (UUID)                       |
| `feedback_text`  | STRING          | Original customer feedback                     |
| `sentiment`      | STRING          | positive, neutral, or negative                 |
| `category`       | STRING          | delivery, product, service, payment, technical |
| `priority_score` | INT64           | Urgency score (1=low, 5=critical)              |
| `keywords`       | ARRAY\<STRING\> | Key terms extracted from feedback              |
| `root_cause`     | STRING          | Identified underlying issue                    |
| `recommendation` | STRING          | Actionable solution                            |
| `summary`        | STRING          | One-sentence summary                           |
| `created_at`     | TIMESTAMP       | Analysis timestamp                             |

## 🧪 Local Development

### Setup Agent Server

```bash
cd adk-agent

# Create .env file
cat > .env << EOF
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=europe-west1
GEMMA_MODEL_NAME=gemma3:4b
OLLAMA_API_BASE=http://localhost:11434
EOF

# Install dependencies (using uv)
uv sync

# Run agent server
python server.py

# Access Web UI
open http://localhost:8080
```

### Setup Backend API

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_CLOUD_PROJECT=your-project-id
export AGENT_URL=http://localhost:8080

# Run backend
python -m app.main

# Access API
open http://localhost:8080/docs
```

### Testing

```bash
# Test agent directly
curl -X POST http://localhost:8080/agents/tanggap_agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Product quality excellent"
  }'

# Test backend API
curl -X POST http://localhost:8080/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": "Delivery was 3 days late"
  }'

# Query data
curl "http://localhost:8080/api/query?limit=5"
```

## 🔐 Environment Variables

### ADK Agent (`adk-agent/.env`)

| Variable                | Description             | Example                   |
| ----------------------- | ----------------------- | ------------------------- |
| `GOOGLE_CLOUD_PROJECT`  | Google Cloud project ID | `your-project-id`         |
| `GOOGLE_CLOUD_LOCATION` | GCP region              | `europe-west1`            |
| `GEMMA_MODEL_NAME`      | Gemma model version     | `gemma3:4b`               |
| `OLLAMA_API_BASE`       | Ollama server URL       | `http://ollama-url:11434` |

### Backend API (`backend/.env`)

| Variable               | Description             | Example                 |
| ---------------------- | ----------------------- | ----------------------- |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID | `your-project-id`       |
| `AGENT_URL`            | ADK Agent server URL    | `http://agent-url:8080` |

### Ollama Backend

| Variable         | Description                    | Example     |
| ---------------- | ------------------------------ | ----------- |
| `MODEL`          | Model to load                  | `gemma3:4b` |
| `OLLAMA_NUM_GPU` | Number of GPUs (999 = use all) | `999`       |

## 📈 Model Selection

The project uses **Gemma 3 4B** for optimal balance between performance and accuracy:

| Model         | Size   | Performance | Issues                   | Status         |
| ------------- | ------ | ----------- | ------------------------ | -------------- |
| gemma3:270m   | 270M   | Fast        | Hallucinations, examples | ❌ Rejected    |
| gemma2:2b     | 2B     | Moderate    | Inconsistent JSON format | ❌ Rejected    |
| **gemma3:4b** | **4B** | **Good**    | **None**                 | ✅ **Current** |

**Why Gemma 3 4B?**

-   Reliable instruction following
-   Consistent JSON output format
-   Accurate sentiment and category classification
-   Good root cause analysis quality
-   Reasonable resource requirements (16GB GPU memory)

## 🎯 Use Cases

### 1. Customer Support Analytics

Analyze incoming support tickets to:

-   Identify trending issues
-   Prioritize critical problems
-   Track sentiment over time
-   Generate actionable insights

### 2. Product Feedback Management

Process user feedback to:

-   Categorize feature requests
-   Identify product quality issues
-   Track customer satisfaction
-   Guide product roadmap decisions

### 3. Service Quality Monitoring

Monitor service feedback to:

-   Detect delivery problems
-   Identify technical issues
-   Measure service quality
-   Improve operational processes

### 4. Real-Time Dashboard

Build analytics dashboards by:

-   Querying BigQuery directly
-   Visualizing sentiment trends
-   Tracking category distribution
-   Monitoring priority scores

## 🏆 Key Benefits

### For Developers

-   **Clean Architecture**: Separation between agent logic and API orchestration
-   **Easy Integration**: RESTful API with clear endpoints
-   **Cloud-Native**: Designed for Google Cloud Run
-   **Scalable**: Handles concurrent requests efficiently

### For Business

-   **Automated Analysis**: Save hours of manual feedback review
-   **Actionable Insights**: Get specific recommendations, not just classifications
-   **Data-Driven Decisions**: Historical data in BigQuery for trend analysis
-   **Cost-Effective**: Serverless architecture scales to zero when not in use

## 🔍 Example Analyses

### Example 1: Technical Issue

**Input:**

```json
{
    "feedback": "Website slow during peak hours"
}
```

**Output:**

```json
{
    "sentiment": "negative",
    "category": "technical",
    "priority_score": 3,
    "keywords": ["website", "slow", "peak hours"],
    "root_cause": "Server capacity issues",
    "recommendation": "Scale server resources",
    "summary": "Website performance degrades during high traffic."
}
```

### Example 2: Delivery Problem

**Input:**

```json
{
    "feedback": "Delivery saya telat 3 hari"
}
```

**Output:**

```json
{
    "sentiment": "negative",
    "category": "delivery",
    "priority_score": 4,
    "keywords": ["delivery", "late", "3 days"],
    "root_cause": "Shipping delay",
    "recommendation": "Improve logistics tracking",
    "summary": "Delivery delayed by 3 days."
}
```

### Example 3: Positive Feedback

**Input:**

```json
{
    "feedback": "Product quality is excellent"
}
```

**Output:**

```json
{
    "sentiment": "positive",
    "category": "product",
    "priority_score": 1,
    "keywords": ["product", "quality", "excellent"],
    "root_cause": "Good manufacturing standards",
    "recommendation": "Maintain current quality",
    "summary": "Customer satisfied with product quality."
}
```

## 🛠️ Technology Stack

| Component           | Technology       | Purpose                        |
| ------------------- | ---------------- | ------------------------------ |
| **Agent Framework** | Google ADK       | AI agent orchestration         |
| **LLM Model**       | Gemma 3 4B       | Natural language understanding |
| **Model Server**    | Ollama           | LLM inference                  |
| **Backend API**     | FastAPI          | REST API endpoints             |
| **Data Storage**    | BigQuery         | Scalable data warehouse        |
| **Deployment**      | Google Cloud Run | Serverless container platform  |
| **Language**        | Python 3.11+     | Core programming language      |
| **HTTP Client**     | httpx            | Async HTTP requests            |

## 📝 License

MIT

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using Google ADK + Gemma 3 4B + BigQuery**
