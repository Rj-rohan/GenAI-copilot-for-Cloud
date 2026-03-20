import json
import os

class CloudTrailCollector:
    """
    Simulates fetching audit logs and activity data from AWS CloudTrail.
    In production, this would call: boto3.client('cloudtrail').lookup_events(...)
    """
    SOURCE_NAME = "AWS CloudTrail"

    def __init__(self, sources_path):
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
