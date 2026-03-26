# Multi-Cloud Implementation Guide

## Overview

The GenAI Cloud Security Copilot now supports **cloud-agnostic** security analysis across:
- **AWS** (Amazon Web Services)
- **Azure** (Microsoft Azure)
- **GCP** (Google Cloud Platform)

## Architecture

### Cloud-Agnostic Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Dashboard                        │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │   AWS    │    │  Azure   │    │   GCP    │              │
│  │ Dashboard│    │ Dashboard│    │ Dashboard│              │
│  └──────────┘    └──────────┘    └──────────┘              │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend API                             │
│  /api/findings?provider=aws|azure|gcp                       │
│  /api/generate (provider: aws|azure|gcp)                    │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Data Collection Layer (Multi-Cloud)             │
│  ┌─────────────┬─────────────┬─────────────┐               │
│  │    AWS      │   Azure     │     GCP     │               │
│  ├─────────────┼─────────────┼─────────────┤               │
│  │ CloudTrail  │ Activity Log│ Audit Logs  │               │
│  │ Config      │ Res. Graph  │ Asset Inv.  │               │
│  │ Cost Exp.   │ Cost Mgmt   │ Billing     │               │
│  │ SecurityHub │ Sec. Center │ SCC         │               │
│  │ CloudWatch  │ Monitor     │ Monitoring  │               │
│  └─────────────┴─────────────┴─────────────┘               │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Unified Resource Model                          │
│  (Cloud-agnostic data structure)                            │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│         Rule Engine & Risk Scoring                          │
│  (Same rules apply across all clouds)                       │
└─────────────────────────────────────────────────────────────┘
```

## Service Mapping

| Category | AWS | Azure | GCP |
|----------|-----|-------|-----|
| **Activity Logs** | CloudTrail | Activity Log | Cloud Audit Logs |
| **Resource Inventory** | AWS Config | Resource Graph | Asset Inventory |
| **Cost Management** | Cost Explorer | Cost Management | Cloud Billing |
| **Security** | Security Hub | Security Center | Security Command Center |
| **Metrics** | CloudWatch | Azure Monitor | Cloud Monitoring |

## Usage

### Generate Data for All Clouds

```bash
cd backend

# Generate for all clouds (30 resources each)
python generate_data_multicloud.py --provider all --count 30

# Generate for specific cloud
python generate_data_multicloud.py --provider aws --count 50
python generate_data_multicloud.py --provider azure --count 50
python generate_data_multicloud.py --provider gcp --count 50
```

### Run Analysis Pipeline

```bash
# Analyze AWS resources
python main.py --provider aws

# Analyze Azure resources
python main.py --provider azure

# Analyze GCP resources
python main.py --provider gcp
```

### Start the Application

```bash
# Backend (Terminal 1)
cd backend
python api.py

# Frontend (Terminal 2)
cd frontend
npm run dev
```

### Switch Between Clouds

In the dashboard UI:
1. Look for the **cloud selector** in the bottom-right corner
2. Click on **AWS**, **Azure**, or **GCP** to switch dashboards
3. Each cloud has its own independent findings and statistics

## File Structure

```
backend/
├── data/
│   ├── cloud_providers.json          # Cloud provider configurations
│   ├── resources_aws.json            # AWS resource inventory
│   ├── resources_azure.json          # Azure resource inventory
│   ├── resources_gcp.json            # GCP resource inventory
│   ├── findings_aws.json             # AWS analysis results
│   ├── findings_azure.json           # Azure analysis results
│   ├── findings_gcp.json             # GCP analysis results
│   └── sources/
│       ├── cloudtrail_aws.json       # AWS activity logs
│       ├── cloudtrail_azure.json     # Azure activity logs
│       ├── cloudtrail_gcp.json       # GCP activity logs
│       ├── config_aws.json           # AWS resource config
│       ├── config_azure.json         # Azure resource config
│       ├── config_gcp.json           # GCP resource config
│       └── ... (cost, security, metrics for each cloud)
│
├── collector/
│   ├── collector_orchestrator.py     # Multi-cloud orchestrator
│   ├── cloudtrail_collector.py       # Activity log collector
│   ├── config_collector.py           # Resource config collector
│   ├── cost_collector.py             # Cost data collector
│   ├── securityhub_collector.py      # Security findings collector
│   └── metrics_collector.py          # Metrics collector
│
├── generate_data_multicloud.py       # Multi-cloud data generator
└── main.py                            # Analysis pipeline

frontend/
├── public/
│   ├── findings_aws.json             # AWS findings (served)
│   ├── findings_azure.json           # Azure findings (served)
│   └── findings_gcp.json             # GCP findings (served)
│
└── src/
    ├── App.jsx                        # Cloud selector
    └── Dashboard.jsx                  # Cloud-aware dashboard
```

## API Endpoints

### Get Findings by Provider
```http
GET /api/findings?provider=aws
GET /api/findings?provider=azure
GET /api/findings?provider=gcp
```

### Generate Data for Provider
```http
POST /api/generate
Content-Type: application/json

{
  "provider": "aws",
  "n_resources": 50
}
```

### Get Available Providers
```http
GET /api/providers

Response:
[
  { "id": "aws", "name": "AWS", "count": 27 },
  { "id": "azure", "name": "Azure", "count": 29 },
  { "id": "gcp", "name": "GCP", "count": 24 }
]
```

## Key Features

### 1. Unified Resource Model
All cloud resources are normalized into a common data structure:
- Resource ID, type, region
- Security posture (encryption, logging, public access)
- Cost and usage metrics
- Compliance violations
- Vulnerabilities and CVEs

### 2. Cloud-Agnostic Rules
The same security rules apply across all clouds:
- Encryption requirements
- Public access restrictions
- Logging compliance
- Cost optimization
- Idle resource detection

### 3. Provider-Specific Naming
Resources are named according to cloud conventions:
- AWS: `ec2-web-server`, `s3-backup-store`, `rds-primary-db`
- Azure: `vm-web-server`, `blob-backup-store`, `sqldb-primary-db`
- GCP: `gce-web-server`, `gcs-backup-store`, `cloudsql-primary-db`

### 4. Region Mapping
Each cloud uses its native region naming:
- AWS: `us-east-1`, `us-west-2`, `eu-west-1`
- Azure: `eastus`, `westus2`, `westeurope`
- GCP: `us-east1`, `us-west1`, `europe-west1`

## Benefits

1. **Single Pane of Glass**: Monitor security across all clouds from one dashboard
2. **Consistent Analysis**: Same risk scoring and rules across all providers
3. **Easy Comparison**: Compare security posture between clouds
4. **Scalable**: Add new cloud providers without changing core logic
5. **Production-Ready**: Designed for real cloud API integration

## Future Enhancements

- [ ] Real-time cloud API integration (boto3, Azure SDK, GCP SDK)
- [ ] Multi-cloud cost comparison
- [ ] Cross-cloud compliance reporting
- [ ] Unified remediation workflows
- [ ] Multi-cloud resource tagging standards
- [ ] Cloud-specific best practices recommendations

## Example Output

### AWS Dashboard
- 27 findings (10 Critical, 12 High, 3 Medium, 2 Low)
- $262/month at risk
- $118 potential savings
- 81 vulnerabilities

### Azure Dashboard
- 29 findings (9 Critical, 11 High, 7 Medium, 2 Low)
- $307/month at risk
- $169 potential savings
- 59 vulnerabilities

### GCP Dashboard
- 24 findings (12 Critical, 7 High, 4 Medium, 1 Low)
- $238/month at risk
- $123 potential savings
- 62 vulnerabilities
