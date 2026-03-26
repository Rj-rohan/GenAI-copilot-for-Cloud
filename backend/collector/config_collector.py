import json
import os

class ConfigCollector:
    """
    Simulates fetching resource inventory and compliance data from cloud providers.
    AWS: Config, Azure: Resource Graph, GCP: Asset Inventory
    """
    SOURCE_NAMES = {
        'aws': 'AWS Config',
        'azure': 'Azure Resource Graph',
        'gcp': 'GCP Asset Inventory'
    }

    def __init__(self, sources_path, provider='aws'):
        self.provider = provider
        self.name = self.SOURCE_NAMES.get(provider, 'Config')
        path = os.path.join(sources_path, f"config_{provider}.json")
        if not os.path.exists(path):
            path = os.path.join(sources_path, "config.json")
        with open(path, 'r') as f:
            self._data = json.load(f)

    def fetch(self, resource_id):
        """Return simulated AWS Config data for a given resource ID."""
        record = self._data.get(resource_id, {})
        tags = record.get("tags", {})
        violations = record.get("compliance_violations", [])
        return {
            "region":                    record.get("region", "us-east-1"),
            "resource_name":             record.get("resource_name", resource_id),
            "tags":                      tags,
            "has_tags":                  len(tags) > 0,
            "created_days_ago":          record.get("created_days_ago", 0),
            "compliance_violations":     violations,
            "compliance_violation_count": len(violations)
        }
