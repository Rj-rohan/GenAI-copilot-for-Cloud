# Cloud Collector Names Reference

## Overview
The GenAI Cloud Security Copilot uses 5 collectors to gather data from cloud providers. Each collector has cloud-specific names that reflect the actual services used in each platform.

---

## 1. Activity Log Collector
**Purpose**: Collects audit logs, failed login attempts, suspicious API calls, and activity history

| Cloud Provider | Service Name | Collector Class |
|---------------|--------------|-----------------|
| **AWS** | AWS CloudTrail | `CloudTrailCollector` |
| **Azure** | Azure Activity Log | `CloudTrailCollector` |
| **GCP** | GCP Cloud Audit Logs | `CloudTrailCollector` |

**Data Collected**:
- Last activity timestamp
- Failed login attempts
- Suspicious API calls
- Regions accessed

**Real API Integration**:
```python
# AWS
import boto3
cloudtrail = boto3.client('cloudtrail')
events = cloudtrail.lookup_events(...)

# Azure
from azure.mgmt.monitor import MonitorManagementClient
activity_logs = monitor_client.activity_logs.list(...)

# GCP
from google.cloud import logging
client = logging.Client()
entries = client.list_entries(...)
```

---

## 2. Resource Inventory Collector
**Purpose**: Collects resource configuration, tags, compliance violations, and metadata

| Cloud Provider | Service Name | Collector Class |
|---------------|--------------|-----------------|
| **AWS** | AWS Config | `ConfigCollector` |
| **Azure** | Azure Resource Graph | `ConfigCollector` |
| **GCP** | GCP Asset Inventory | `ConfigCollector` |

**Data Collected**:
- Resource name and region
- Tags and metadata
- Compliance violations
- Creation timestamp

**Real API Integration**:
```python
# AWS
import boto3
config = boto3.client('config')
resources = config.list_discovered_resources(...)

# Azure
from azure.mgmt.resourcegraph import ResourceGraphClient
query_result = resource_graph_client.resources(...)

# GCP
from google.cloud import asset_v1
client = asset_v1.AssetServiceClient()
assets = client.list_assets(...)
```

---

## 3. Cost Management Collector
**Purpose**: Collects billing data, cost trends, savings opportunities, and rightsizing recommendations

| Cloud Provider | Service Name | Collector Class |
|---------------|--------------|-----------------|
| **AWS** | AWS Cost Explorer | `CostCollector` |
| **Azure** | Azure Cost Management | `CostCollector` |
| **GCP** | GCP Cloud Billing | `CostCollector` |

**Data Collected**:
- Monthly cost
- Cost trend percentage
- Savings potential
- Rightsizing recommendations

**Real API Integration**:
```python
# AWS
import boto3
ce = boto3.client('ce')
cost_data = ce.get_cost_and_usage(...)

# Azure
from azure.mgmt.costmanagement import CostManagementClient
usage = cost_client.query.usage(...)

# GCP
from google.cloud import billing
client = billing.CloudBillingClient()
billing_info = client.get_billing_info(...)
```

---

## 4. Security Findings Collector
**Purpose**: Collects vulnerabilities, CVEs, open ports, and security compliance scores

| Cloud Provider | Service Name | Collector Class |
|---------------|--------------|-----------------|
| **AWS** | AWS Security Hub | `SecurityHubCollector` |
| **Azure** | Azure Security Center | `SecurityHubCollector` |
| **GCP** | GCP Security Command Center | `SecurityHubCollector` |

**Data Collected**:
- Vulnerability count
- CVE count
- Open ports
- Compliance score
- SSH/RDP exposure

**Real API Integration**:
```python
# AWS
import boto3
securityhub = boto3.client('securityhub')
findings = securityhub.get_findings(...)

# Azure
from azure.mgmt.security import SecurityCenter
alerts = security_client.alerts.list(...)

# GCP
from google.cloud import securitycenter
client = securitycenter.SecurityCenterClient()
findings = client.list_findings(...)
```

---

## 5. Performance Metrics Collector
**Purpose**: Collects CPU, memory, network, and disk utilization metrics

| Cloud Provider | Service Name | Collector Class |
|---------------|--------------|-----------------|
| **AWS** | AWS CloudWatch | `MetricsCollector` |
| **Azure** | Azure Monitor | `MetricsCollector` |
| **GCP** | GCP Cloud Monitoring | `MetricsCollector` |

**Data Collected**:
- CPU average utilization
- Memory average utilization
- Network traffic (GB)
- Disk utilization

**Real API Integration**:
```python
# AWS
import boto3
cloudwatch = boto3.client('cloudwatch')
metrics = cloudwatch.get_metric_statistics(...)

# Azure
from azure.mgmt.monitor import MonitorManagementClient
metrics = monitor_client.metrics.list(...)

# GCP
from google.cloud import monitoring_v3
client = monitoring_v3.MetricServiceClient()
results = client.list_time_series(...)
```

---

## Complete Mapping Table

| # | Category | AWS | Azure | GCP |
|---|----------|-----|-------|-----|
| 1 | **Activity Logs** | AWS CloudTrail | Azure Activity Log | GCP Cloud Audit Logs |
| 2 | **Resource Inventory** | AWS Config | Azure Resource Graph | GCP Asset Inventory |
| 3 | **Cost Management** | AWS Cost Explorer | Azure Cost Management | GCP Cloud Billing |
| 4 | **Security Findings** | AWS Security Hub | Azure Security Center | GCP Security Command Center |
| 5 | **Performance Metrics** | AWS CloudWatch | Azure Monitor | GCP Cloud Monitoring |

---

## File Structure

### Data Files by Provider

```
backend/data/sources/
├── cloudtrail_aws.json       # AWS CloudTrail data
├── cloudtrail_azure.json     # Azure Activity Log data
├── cloudtrail_gcp.json       # GCP Cloud Audit Logs data
│
├── config_aws.json           # AWS Config data
├── config_azure.json         # Azure Resource Graph data
├── config_gcp.json           # GCP Asset Inventory data
│
├── cost_aws.json             # AWS Cost Explorer data
├── cost_azure.json           # Azure Cost Management data
├── cost_gcp.json             # GCP Cloud Billing data
│
├── securityhub_aws.json      # AWS Security Hub data
├── securityhub_azure.json    # Azure Security Center data
├── securityhub_gcp.json      # GCP Security Command Center data
│
├── metrics_aws.json          # AWS CloudWatch data
├── metrics_azure.json        # Azure Monitor data
└── metrics_gcp.json          # GCP Cloud Monitoring data
```

---

## Console Output Example

### AWS
```
[1] Data Collection Layer
----------------------------------------
  Cloud Provider: Amazon Web Services
  Services:
    - AWS CloudTrail
    - AWS Config
    - AWS Cost Explorer
    - AWS Security Hub
    - AWS CloudWatch
  Collecting from 5 data sources:
    [OK] AWS CloudTrail
    [OK] AWS Config
    [OK] AWS Cost Explorer
    [OK] AWS Security Hub
    [OK] AWS CloudWatch
```

### Azure
```
[1] Data Collection Layer
----------------------------------------
  Cloud Provider: Microsoft Azure
  Services:
    - Azure Activity Log
    - Azure Resource Graph
    - Azure Cost Management
    - Azure Security Center
    - Azure Monitor
  Collecting from 5 data sources:
    [OK] Azure Activity Log
    [OK] Azure Resource Graph
    [OK] Azure Cost Management
    [OK] Azure Security Center
    [OK] Azure Monitor
```

### GCP
```
[1] Data Collection Layer
----------------------------------------
  Cloud Provider: Google Cloud Platform
  Services:
    - GCP Cloud Audit Logs
    - GCP Asset Inventory
    - GCP Cloud Billing
    - GCP Security Command Center
    - GCP Cloud Monitoring
  Collecting from 5 data sources:
    [OK] GCP Cloud Audit Logs
    [OK] GCP Asset Inventory
    [OK] GCP Cloud Billing
    [OK] GCP Security Command Center
    [OK] GCP Cloud Monitoring
```

---

## Usage in Code

### Accessing Collector Names
```python
from collector.cloudtrail_collector import CloudTrailCollector

# AWS
collector = CloudTrailCollector(sources_path, provider='aws')
print(collector.name)  # Output: "AWS CloudTrail"

# Azure
collector = CloudTrailCollector(sources_path, provider='azure')
print(collector.name)  # Output: "Azure Activity Log"

# GCP
collector = CloudTrailCollector(sources_path, provider='gcp')
print(collector.name)  # Output: "GCP Cloud Audit Logs"
```

### All Collector Names
```python
from collector.cloudtrail_collector import CloudTrailCollector
from collector.config_collector import ConfigCollector
from collector.cost_collector import CostCollector
from collector.securityhub_collector import SecurityHubCollector
from collector.metrics_collector import MetricsCollector

provider = 'azure'  # or 'aws' or 'gcp'

collectors = [
    CloudTrailCollector(sources_path, provider),
    ConfigCollector(sources_path, provider),
    CostCollector(sources_path, provider),
    SecurityHubCollector(sources_path, provider),
    MetricsCollector(sources_path, provider)
]

for collector in collectors:
    print(f"[OK] {collector.name}")
```

---

## Benefits of Cloud-Specific Naming

1. **Clarity**: Users immediately understand which cloud service is being used
2. **Accuracy**: Names match actual cloud provider terminology
3. **Documentation**: Easy to map to official cloud documentation
4. **Debugging**: Clear logs showing which service failed or succeeded
5. **Production-Ready**: Names align with real API services for easy integration

---

## Summary

Each of the 5 collectors has been designed to be **cloud-agnostic** while displaying **cloud-specific names** to users. This provides:

- ✅ Consistent internal architecture
- ✅ Cloud-native naming in UI and logs
- ✅ Easy mapping to real cloud APIs
- ✅ Clear documentation for each provider
- ✅ Production-ready design

The system automatically selects the correct service name based on the `provider` parameter, making it seamless to work with any cloud platform.
