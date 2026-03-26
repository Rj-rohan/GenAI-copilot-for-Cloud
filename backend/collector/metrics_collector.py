import json
import os

class MetricsCollector:
    """
    Simulates fetching utilization metrics from cloud providers.
    AWS: CloudWatch, Azure: Azure Monitor, GCP: Cloud Monitoring
    """
    SOURCE_NAMES = {
        'aws': 'AWS CloudWatch',
        'azure': 'Azure Monitor',
        'gcp': 'GCP Cloud Monitoring'
    }

    def __init__(self, sources_path, provider='aws'):
        self.provider = provider
        self.name = self.SOURCE_NAMES.get(provider, 'CloudWatch')
        path = os.path.join(sources_path, f"metrics_{provider}.json")
        if not os.path.exists(path):
            path = os.path.join(sources_path, "metrics.json")
        with open(path, 'r') as f:
            self._data = json.load(f)

    def fetch(self, resource_id):
        """Return simulated CloudWatch metrics for a given resource ID."""
        record = self._data.get(resource_id, {})
        return {
            "cpu_avg":          record.get("cpu_avg", 0.0),
            "memory_avg":       record.get("memory_avg", 0.0),
            "network_in_gb":    record.get("network_in_gb", 0.0),
            "disk_utilization": record.get("disk_utilization", 0.0)
        }
