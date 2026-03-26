# 🏗️ Multi-Cloud Security Copilot - Architecture & How It Works

## 📋 Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Data Flow](#data-flow)
4. [Backend Components](#backend-components)
5. [Frontend Components](#frontend-components)
6. [Multi-Cloud Support](#multi-cloud-support)
7. [GenAI Copilot](#genai-copilot)
8. [API Endpoints](#api-endpoints)
9. [Security & Best Practices](#security--best-practices)

---

## Overview

**Multi-Cloud Security Copilot** is a GenAI-powered cloud security and FinOps platform that analyzes resources across **AWS, Azure, and GCP** using a unified rule engine and provides AI-driven remediation guidance.

### Hackathon Compliance
✅ **Misconfiguration Detection** - 15 rules detect security gaps  
✅ **Risk Prioritization** - Transparent scoring with CRITICAL/HIGH/MEDIUM/LOW  
✅ **Cost Optimization** - Identifies idle/unused resources, calculates savings  
✅ **Actionable Insights** - Cloud-specific CLI commands for remediation  
✅ **Dashboard & Reports** - Interactive UI with charts, CSV export  
✅ **Cloud-Native** - Containerized with Docker  
✅ **Platform-Agnostic** - Works with AWS, Azure, GCP  
✅ **Simulated Datasets** - No real cloud credentials needed  
✅ **Logic-Focused** - Core analysis works without external APIs  

### Key Features
- ✅ Multi-cloud support (AWS, Azure, GCP)
- ✅ 15 security/compliance/cost rules
- ✅ Risk scoring with transparent formula
- ✅ GenAI copilot with cloud-specific CLI commands (optional)
- ✅ Priority action queue
- ✅ Real-time data generation
- ✅ Interactive dashboard with charts

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Dashboard   │  │   Copilot    │  │ Cloud Switch │          │
│  │  (Charts)    │  │  (GenAI)     │  │ (AWS/Az/GCP) │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (Python/Flask)                      │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                      API Layer (api.py)                     │ │
│  │  /api/findings  /api/copilot  /api/generate  /api/health   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                    │
│  ┌───────────────────────────┴───────────────────────────────┐  │
│  │                                                             │  │
│  │  ┌──────────────────┐         ┌──────────────────┐        │  │
│  │  │  Data Generator  │         │  GenAI Copilot   │        │  │
│  │  │  (Simulated)     │         │  (Gemini AI)     │        │  │
│  │  └──────────────────┘         └──────────────────┘        │  │
│  │           │                             │                   │  │
│  │           ▼                             ▼                   │  │
│  │  ┌──────────────────┐         ┌──────────────────┐        │  │
│  │  │ Collector Layer  │         │ Context Builder  │        │  │
│  │  │ (5 collectors)   │         │ Prompt Generator │        │  │
│  │  └──────────────────┘         └──────────────────┘        │  │
│  │           │                             │                   │  │
│  │           ▼                             ▼                   │  │
│  │  ┌──────────────────┐         ┌──────────────────┐        │  │
│  │  │   Rule Engine    │         │  LLM Connector   │        │  │
│  │  │  (15 rules)      │         │  (Multi-key)     │        │  │
│  │  └──────────────────┘         └──────────────────┘        │  │
│  │           │                                                 │  │
│  │           ▼                                                 │  │
│  │  ┌──────────────────┐                                      │  │
│  │  │  Risk Scorer     │                                      │  │
│  │  │  Insight Gen     │                                      │  │
│  │  └──────────────────┘                                      │  │
│  │           │                                                 │  │
│  │           ▼                                                 │  │
│  │  ┌──────────────────────────────────────────────┐         │  │
│  │  │         Findings JSON (per cloud)            │         │  │
│  │  │  findings_aws.json / azure.json / gcp.json   │         │  │
│  │  └──────────────────────────────────────────────┘         │  │
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. Data Generation Flow
```
User clicks "Generate Data"
    ↓
Frontend → POST /api/generate (provider: aws/azure/gcp)
    ↓
Backend: generate_data_multicloud.py
    ↓
Generate 30-50 simulated resources
    ↓
5 Collectors gather data:
  - Activity (CloudTrail/Activity Log/Audit Logs)
  - Config (AWS Config/Resource Graph/Asset Inventory)
  - Cost (Cost Explorer/Cost Management/Cloud Billing)
  - Security (SecurityHub/Security Center/SCC)
  - Metrics (CloudWatch/Azure Monitor/Cloud Monitoring)
    ↓
Rule Engine evaluates 15 rules
    ↓
Risk Scorer calculates scores
    ↓
Insight Generator creates findings
    ↓
Save to data/findings_{provider}.json
    ↓
Copy to frontend/public/findings_{provider}.json
    ↓
Frontend auto-refreshes
```

### 2. GenAI Copilot Flow
```
User types query: "fix r3"
    ↓
Frontend → POST /api/copilot (query, provider)
    ↓
CopilotEngine (provider-aware)
    ↓
QueryHandler parses query type (fix/explain/summary)
    ↓
ContextBuilder loads findings_{provider}.json
    ↓
PromptGenerator creates cloud-specific prompt
  - Uses cloud service names (CloudTrail vs Activity Log)
  - Includes pre-computed CLI commands
    ↓
LLMConnector sends to Gemini AI
  - Try Key 1 → If quota exceeded → Try Key 2
    ↓
Gemini generates response with CLI commands
    ↓
Return to frontend
    ↓
Display formatted response
```

---

## Backend Components

### 1. Data Generation (`generate_data_multicloud.py`)
**Purpose:** Generate simulated cloud resources with realistic security issues

**Features:**
- Cloud-specific resource naming (ec2/vm/gce, s3/blob/gcs)
- Realistic issue distribution (public resources, unencrypted, idle)
- 5 data sources per resource
- Configurable count (default: 30-50)

**Usage:**
```bash
python generate_data_multicloud.py --provider aws --count 30
python generate_data_multicloud.py --provider all --count 50
```

### 2. Collector Layer (`collector/`)
**Purpose:** Simulate data from 5 cloud services

**Collectors:**
- `cloudtrail_collector.py` - Activity logs, failed logins, suspicious APIs
- `config_collector.py` - Resource metadata, tags, compliance violations
- `cost_collector.py` - Monthly cost, trends, savings potential
- `securityhub_collector.py` - Vulnerabilities, CVEs, open ports
- `metrics_collector.py` - CPU, memory, disk, network usage

**Orchestrator:** `collector_orchestrator.py` - Coordinates all collectors

### 3. Rule Engine (`engine/`)
**Purpose:** Evaluate resources against 15 security/compliance/cost rules

**Components:**
- `rule_loader.py` - Loads rules from rules.json
- `rule_evaluator.py` - Evaluates resources against rules
- `risk_scorer.py` - Calculates risk scores using weighted formula
- `insight_generator.py` - Generates human-readable findings

**Risk Scoring Formula:**
```
(Security Rules × 4) + (Compliance × 3) + (Access × 3) + (Cost ÷ 5) 
+ Idle Penalty × 1.5 (if public) = Risk Score

Thresholds:
- CRITICAL: ≥ 100
- HIGH: ≥ 60
- MEDIUM: ≥ 30
- LOW: < 30
```

### 4. GenAI Copilot (`copilot/`)
**Purpose:** AI-powered security assistant with cloud-specific guidance

**Components:**
- `copilot_engine.py` - Main orchestrator
- `query_handler.py` - Parses user queries
- `context_builder.py` - Loads findings for specific cloud
- `prompt_generator.py` - Creates cloud-specific prompts
- `llm_connector.py` - Connects to Gemini AI with multi-key support
- `cli_commands_multicloud.py` - Cloud-specific CLI remediation commands

**Multi-Key Support:**
- Supports 1-4 Gemini API keys
- Automatic rotation on quota exhaustion
- Graceful fallback to mock mode

### 5. API Layer (`api.py`)
**Purpose:** REST API for frontend communication

**Endpoints:**
- `GET /api/findings?provider=aws` - Get findings for cloud
- `POST /api/copilot` - Query GenAI copilot
- `POST /api/generate` - Generate new data
- `GET /api/providers` - List available clouds
- `GET /api/health` - Health check

---

## Frontend Components

### 1. App Shell (`App.jsx`)
**Purpose:** Main application layout with sidebar and cloud selector

**Features:**
- Sidebar navigation (Dashboard, Copilot)
- Cloud selector (AWS, Azure, GCP buttons)
- Breadcrumb navigation
- User avatar

### 2. Dashboard (`Dashboard.jsx`)
**Purpose:** Security overview with charts and findings table

**Features:**
- Stat tiles (Total, Critical, High, Medium, Low, Cost, Savings)
- Priority action queue (Top 5 critical/high)
- Risk distribution donut chart
- Cost & savings bar chart
- Compliance overview gauge
- Sortable/filterable findings table
- Detail drawer with score breakdown
- Export to CSV
- Generate/Refresh buttons

### 3. Copilot (`Copilot.jsx`)
**Purpose:** GenAI chat interface for security queries

**Features:**
- Quick command buttons
- Chat interface with markdown rendering
- Cloud-aware (sends provider to backend)
- Real-time responses
- Code block formatting
- Loading states

---

## Multi-Cloud Support

### Cloud-Specific Naming

| Component | AWS | Azure | GCP |
|-----------|-----|-------|-----|
| Compute | ec2-web-server | vm-web-server | gce-web-server |
| Storage | s3-backup-store | blob-backup-store | gcs-backup-store |
| Database | rds-primary-db | sqldb-primary-db | cloudsql-primary-db |
| Network | alb-public-lb | lb-public-lb | gclb-public-lb |

### Service Name Mapping

| Category | AWS | Azure | GCP |
|----------|-----|-------|-----|
| Activity | CloudTrail | Activity Log | Cloud Audit Logs |
| Config | AWS Config | Resource Graph | Asset Inventory |
| Cost | Cost Explorer | Cost Management | Cloud Billing |
| Security | SecurityHub | Security Center | Security Command Center |
| Metrics | CloudWatch | Azure Monitor | Cloud Monitoring |

### CLI Commands

**AWS:**
```bash
aws ec2 stop-instances --instance-ids i-12345
aws s3api put-public-access-block --bucket my-bucket
```

**Azure:**
```bash
az vm deallocate --name my-vm --resource-group my-rg
az storage account update --name mystorageacct --allow-blob-public-access false
```

**GCP:**
```bash
gcloud compute instances stop my-instance --zone=us-east1-b
gsutil iam ch -d allUsers:objectViewer gs://my-bucket
```

---

## GenAI Copilot

### Architecture
```
User Query → Query Handler → Context Builder → Prompt Generator
                                                      ↓
                                              Cloud-Specific Prompt
                                                      ↓
                                              LLM Connector
                                                      ↓
                                         Try Key 1 → Gemini API
                                              ↓ (quota exceeded)
                                         Try Key 2 → Gemini API
                                              ↓
                                         Response with CLI
                                              ↓
                                         Format & Display
```

### Query Types
- **explain** - Explain why resource is risky
- **fix** - Get remediation steps with CLI commands
- **filter** - Show filtered findings (critical, high, cost, security)
- **summary** - Executive summary report
- **cost** - FinOps cost optimization report

### Multi-Key Rotation
```python
# .env configuration
GEMINI_API_KEY=primary_key
GEMINI_API_KEY_1=fallback_key_1
GEMINI_API_KEY_2=fallback_key_2

# Automatic rotation on quota errors
[LLM] Gemini key 1 quota exceeded, rotating...
[LLM] Switched to Gemini key 2
```

**Benefits:**
- 2 keys = 30 requests/min (2 × 15)
- 3 keys = 45 requests/min (3 × 15)
- High availability
- No manual intervention

---

## API Endpoints

### GET /api/findings
**Purpose:** Get findings for specific cloud provider

**Request:**
```
GET /api/findings?provider=aws
```

**Response:**
```json
[
  {
    "resource_id": "r1",
    "resource_name": "ec2-web-server-01",
    "resource_type": "compute",
    "region": "us-east-1",
    "priority": "CRITICAL",
    "risk_score": 145,
    "issues": ["Public resource detected", "Encryption disabled"],
    "cost": 15,
    "savings_potential": 12.5,
    "cli_fixes": { ... }
  }
]
```

### POST /api/copilot
**Purpose:** Query GenAI copilot

**Request:**
```json
{
  "query": "fix r3",
  "provider": "aws"
}
```

**Response:**
```json
{
  "query": "fix r3",
  "query_type": "fix",
  "response": "**ANALYSIS**\nRemediation plan for r3...\n\n**AWS CLI COMMANDS**\n```bash\naws ec2 stop-instances --instance-ids i-12345\n```",
  "context_count": 1
}
```

### POST /api/generate
**Purpose:** Generate new data for cloud provider

**Request:**
```json
{
  "provider": "aws",
  "n_resources": 50
}
```

**Response:**
```json
{
  "success": true,
  "n_resources": 50,
  "provider": "aws",
  "message": "Generated 50 resources for AWS and ran analysis pipeline."
}
```

### GET /api/health
**Purpose:** Health check and GenAI status

**Response:**
```json
{
  "status": "healthy",
  "genai": "gemini",
  "model": "gemini-2.5-flash"
}
```

---

## Security & Best Practices

### API Key Management
- ✅ Store keys in `.env` file (not committed to Git)
- ✅ Use multiple keys for high availability
- ✅ Automatic rotation on quota exhaustion
- ✅ Keys never exposed in logs or code

### Data Security
- ✅ Simulated data only (no real cloud credentials)
- ✅ No PII or sensitive information
- ✅ All data stored locally

### Code Quality
- ✅ Modular architecture
- ✅ Separation of concerns
- ✅ Error handling and fallbacks
- ✅ Logging for monitoring

### Performance
- ✅ Efficient data generation
- ✅ Caching of findings
- ✅ Lazy loading in frontend
- ✅ Optimized API calls

---

## Quick Start

### 1. Setup API Keys
```bash
cd backend
cp .env.example .env
# Edit .env and add GEMINI_API_KEY
```

### 2. Generate Data
```bash
python generate_data_multicloud.py --provider all --count 30
python main.py --provider azure
python main.py --provider gcp
copy data\findings_*.json ..\frontend\public\
```

### 3. Start Backend
```bash
python api.py
```

### 4. Start Frontend
```bash
cd ..\frontend
npm run dev
```

### 5. Open Browser
```
http://localhost:5173
```

---

## Technology Stack

**Backend:**
- Python 3.11+
- Flask (REST API)
- Google Generative AI (Gemini)
- python-dotenv (Environment variables)

**Frontend:**
- React 18
- Vite (Build tool)
- CSS3 (Custom styling)

**Data:**
- JSON (Findings storage)
- Simulated cloud data

---

## File Structure

```
copilot-aws/
├── backend/
│   ├── collector/          # Data collectors (5 services)
│   ├── copilot/            # GenAI copilot components
│   ├── engine/             # Rule engine & risk scoring
│   ├── models/             # Data models
│   ├── data/               # Generated findings & rules
│   ├── .env                # API keys (not in Git)
│   ├── .env.example        # Template
│   ├── api.py              # REST API
│   ├── main.py             # Analysis pipeline
│   ├── generate_data_multicloud.py  # Data generator
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main app shell
│   │   ├── Dashboard.jsx   # Security dashboard
│   │   └── Copilot.jsx     # GenAI chat
│   ├── public/
│   │   └── findings_*.json # Findings data
│   └── package.json        # Node dependencies
├── .gitignore
├── README.md               # Quick start guide
└── ARCHITECTURE.md         # This file
```

---

## Summary

**Multi-Cloud Security Copilot** is a production-ready platform that:
- ✅ Analyzes cloud resources across AWS, Azure, and GCP
- ✅ Uses 15 security/compliance/cost rules
- ✅ Provides AI-powered remediation guidance
- ✅ Generates cloud-specific CLI commands
- ✅ Supports multiple API keys for high availability
- ✅ Offers interactive dashboard with charts
- ✅ Enables real-time data generation

**Perfect for demos, learning, and prototyping cloud security solutions!** 🚀
