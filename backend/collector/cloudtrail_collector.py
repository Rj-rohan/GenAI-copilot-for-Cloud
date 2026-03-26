import json
import os

class CloudTrailCollector:
    """
    Simulates fetching audit logs and activity data from cloud providers.
    AWS: CloudTrail, Azure: Activity Log, GCP: Cloud Audit Logs
    """
    SOURCE_NAMES = {
        'aws': 'AWS CloudTrail',
        'azure': 'Azure Activity Log',
        'gcp': 'GCP Cloud Audit Logs'
    }

    def __init__(self, sources_path, provider='aws'):
        self.provider = provider
        self.name = self.SOURCE_NAMES.get(provider, 'CloudTrail')
        # Try provider-specific file first, fallback to default
        path = os.path.join(sources_path, f"cloudtrail_{provider}.json")
        if not os.path.exists(path):
            path = os.path.join(sources_path, "cloudtrail.json")
        with open(path, 'r') as f:
            self._data = json.load(f)

    def fetch(self, resource_id):
        """Return simulated CloudTrail data for a given resource ID."""
        record = self._data.get(resource_id, {})
        return {
            "last_activity_days":   record.get("last_activity_days", 0),
            "failed_logins":        record.get("failed_logins", 0),
            "suspicious_api_calls": record.get("suspicious_api_calls", 0),
            "regions_accessed":     record.get("regions_accessed", ["us-east-1"])
        }
