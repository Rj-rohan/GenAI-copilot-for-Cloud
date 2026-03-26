import json
import os

class CostCollector:
    """
    Simulates fetching billing and cost optimization data from cloud providers.
    AWS: Cost Explorer, Azure: Cost Management, GCP: Cloud Billing
    """
    SOURCE_NAMES = {
        'aws': 'AWS Cost Explorer',
        'azure': 'Azure Cost Management',
        'gcp': 'GCP Cloud Billing'
    }

    def __init__(self, sources_path, provider='aws'):
        self.provider = provider
        self.name = self.SOURCE_NAMES.get(provider, 'Cost Explorer')
        path = os.path.join(sources_path, f"cost_{provider}.json")
        if not os.path.exists(path):
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
