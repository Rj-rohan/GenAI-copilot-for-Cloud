import json
import os

class SecurityHubCollector:
    """
    Simulates fetching vulnerability and compliance findings from cloud providers.
    AWS: SecurityHub, Azure: Security Center, GCP: Security Command Center
    """
    SOURCE_NAMES = {
        'aws': 'AWS Security Hub',
        'azure': 'Azure Security Center',
        'gcp': 'GCP Security Command Center'
    }

    def __init__(self, sources_path, provider='aws'):
        self.provider = provider
        self.name = self.SOURCE_NAMES.get(provider, 'Security Hub')
        path = os.path.join(sources_path, f"securityhub_{provider}.json")
        if not os.path.exists(path):
            path = os.path.join(sources_path, "securityhub.json")
        with open(path, 'r') as f:
            self._data = json.load(f)

    def fetch(self, resource_id, is_public=False):
        """Return simulated SecurityHub data for a given resource ID."""
        record = self._data.get(resource_id, {})
        open_ports = record.get("open_ports", [])
        return {
            "vuln_count":       record.get("vuln_count", 0),
            "open_ports":       open_ports,
            "compliance_score": record.get("compliance_score", 100),
            "cve_count":        record.get("cve_count", 0),
            "ssh_exposed":      (22 in open_ports) and is_public,
            "rdp_exposed":      (3389 in open_ports) and is_public
        }
