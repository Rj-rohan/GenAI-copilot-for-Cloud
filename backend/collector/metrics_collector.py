import json
import os

class MetricsCollector:
    """
    Simulates fetching utilization metrics from AWS CloudWatch.
    In production, this would call: boto3.client('cloudwatch').get_metric_statistics(...)
    """
    SOURCE_NAME = "AWS CloudWatch Metrics"

    def __init__(self, sources_path):
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
