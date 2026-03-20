import json
import os

class CostCollector:
    """
    Simulates fetching billing and cost optimization data from AWS Cost Explorer.
    In production, this would call: boto3.client('ce').get_cost_and_usage(...)
    """
    SOURCE_NAME = "AWS Cost Explorer"

    def __init__(self, sources_path):
        path = os.path.join(sources_path, "cost.json")
        with open(path, 'r') as f:
            self._data = json.load(f)

    def fetch(self, resource_id):
        """Return simulated Cost Explorer data for a given resource ID."""
        record = self._data.get(resource_id, {})
        return {
            "monthly_cost":      record.get("monthly_cost", 0),
            "cost_trend_pct":    record.get("cost_trend_pct", 0.0),
            "savings_potential": record.get("savings_potential", 0.0),
            "rightsizing":       record.get("rightsizing", "none")
        }
