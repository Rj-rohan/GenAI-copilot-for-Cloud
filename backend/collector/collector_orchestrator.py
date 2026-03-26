import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collector.cloudtrail_collector import CloudTrailCollector
from collector.config_collector import ConfigCollector
from collector.cost_collector import CostCollector
from collector.securityhub_collector import SecurityHubCollector
from collector.metrics_collector import MetricsCollector
from models.resource import Resource


class CollectorOrchestrator:
    """
    Orchestrates data collection from all 5 cloud data sources and merges
    them into a unified Resource model for the analyzer engine.

    Data Flow:
        CloudTrail + Config + Cost + SecurityHub + Metrics
                          ↓
                  Unified Resource Model
                          ↓
                    Analyzer Engine
    """

    CLOUD_SERVICES = {
        'aws': [
            "AWS CloudTrail     - Activity logs, failed logins, API calls",
            "AWS Config         - Resource inventory, tags, compliance",
            "AWS Cost Explorer  - Billing, cost trends, savings opportunities",
            "AWS SecurityHub    - Vulnerabilities, open ports, CVEs",
            "AWS CloudWatch     - CPU, memory, network, disk metrics"
        ],
        'azure': [
            "Activity Log       - Activity logs, failed logins, API calls",
            "Resource Graph     - Resource inventory, tags, compliance",
            "Cost Management    - Billing, cost trends, savings opportunities",
            "Security Center    - Vulnerabilities, open ports, CVEs",
            "Azure Monitor      - CPU, memory, network, disk metrics"
        ],
        'gcp': [
            "Cloud Audit Logs   - Activity logs, failed logins, API calls",
            "Asset Inventory    - Resource inventory, tags, compliance",
            "Cloud Billing      - Billing, cost trends, savings opportunities",
            "Security Command   - Vulnerabilities, open ports, CVEs",
            "Cloud Monitoring   - CPU, memory, network, disk metrics"
        ]
    }

    def __init__(self, sources_path, inventory_path, provider='aws'):
        self.provider = provider
        self.cloudtrail   = CloudTrailCollector(sources_path, provider)
        self.config       = ConfigCollector(sources_path, provider)
        self.cost         = CostCollector(sources_path, provider)
        self.securityhub  = SecurityHubCollector(sources_path, provider)
        self.metrics      = MetricsCollector(sources_path, provider)

        with open(inventory_path, 'r') as f:
            self._inventory = json.load(f)

    def collect(self):
        """
        Pull data from all 5 sources for each resource and merge into
        enriched Resource objects.
        Returns a list of Resource instances ready for the rule engine.
        """
        print("  Collecting from 5 data sources:")
        print(f"    [OK] {self.cloudtrail.name}")
        print(f"    [OK] {self.config.name}")
        print(f"    [OK] {self.cost.name}")
        print(f"    [OK] {self.securityhub.name}")
        print(f"    [OK] {self.metrics.name}")

        resources = []
        for item in self._inventory:
            rid        = item["id"]
            is_public  = item.get("public", False)

            ct   = self.cloudtrail.fetch(rid)
            cfg  = self.config.fetch(rid)
            cost = self.cost.fetch(rid)
            sh   = self.securityhub.fetch(rid, is_public=is_public)
            met  = self.metrics.fetch(rid)

            resource = Resource(
                # ── Base inventory (AWS Config / resource list) ──────────
                id          = rid,
                type        = item["type"],
                usage       = item["usage"],
                public      = is_public,
                encrypted   = item.get("encrypted", True),
                cost        = item["cost"],
                logging     = item.get("logging", True),
                role        = item.get("role", "user"),

                # ── AWS Config ───────────────────────────────────────────
                region                    = cfg["region"],
                resource_name             = cfg["resource_name"],
                tags                      = cfg["tags"],
                has_tags                  = cfg["has_tags"],
                created_days_ago          = cfg["created_days_ago"],
                compliance_violations     = cfg["compliance_violations"],
                compliance_violation_count= cfg["compliance_violation_count"],

                # ── AWS CloudTrail ───────────────────────────────────────
                last_activity_days   = ct["last_activity_days"],
                failed_logins        = ct["failed_logins"],
                suspicious_api_calls = ct["suspicious_api_calls"],
                regions_accessed     = ct["regions_accessed"],

                # ── AWS Cost Explorer ────────────────────────────────────
                monthly_cost      = cost["monthly_cost"],
                cost_trend_pct    = cost["cost_trend_pct"],
                savings_potential = cost["savings_potential"],
                rightsizing       = cost["rightsizing"],

                # ── AWS SecurityHub ──────────────────────────────────────
                vuln_count       = sh["vuln_count"],
                open_ports       = sh["open_ports"],
                compliance_score = sh["compliance_score"],
                cve_count        = sh["cve_count"],
                ssh_exposed      = sh["ssh_exposed"],
                rdp_exposed      = sh["rdp_exposed"],

                # ── AWS CloudWatch Metrics ───────────────────────────────
                cpu_avg          = met["cpu_avg"],
                memory_avg       = met["memory_avg"],
                network_in_gb    = met["network_in_gb"],
                disk_utilization = met["disk_utilization"]
            )
            resources.append(resource)

        print(f"\n  Unified Data Model: {len(resources)} resources merged from 5 sources")
        return resources
