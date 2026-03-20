import json
import os

class ContextBuilder:
    def __init__(self, findings_path=None):
        if findings_path is None:
            findings_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data', 'findings.json'
            )
        
        with open(findings_path, 'r', encoding='utf-8') as f:
            self.findings = json.load(f)

    def build_context(self, parsed_query):
        filters = parsed_query['filters']
        resource_id = parsed_query['resource_id']
        
        if resource_id:
            return self._get_resource_context(resource_id)
        
        filtered = self._apply_filters(filters)
        
        return {
            'findings': filtered,
            'count': len(filtered),
            'filters_applied': filters
        }

    def _get_resource_context(self, resource_id):
        for finding in self.findings:
            if finding['resource_id'] == resource_id:
                return {
                    'findings': [finding],
                    'count': 1,
                    'resource_id': resource_id
                }
        return {'findings': [], 'count': 0}

    def _apply_filters(self, filters):
        filtered = self.findings
        
        if 'priority' in filters:
            filtered = [f for f in filtered if f['priority'] == filters['priority']]
        
        if 'category' in filters:
            filtered = [f for f in filtered if filters['category'] in f['categories']]
        
        if 'resource_type' in filters:
            filtered = [f for f in filtered if f['resource_type'] == filters['resource_type']]
        
        return filtered

    def get_summary_stats(self):
        total    = len(self.findings)
        critical = len([f for f in self.findings if f['priority'] == 'CRITICAL'])
        high     = len([f for f in self.findings if f['priority'] == 'HIGH'])
        medium   = len([f for f in self.findings if f['priority'] == 'MEDIUM'])
        low      = len([f for f in self.findings if f['priority'] == 'LOW'])
        total_cost = sum(f['cost'] for f in self.findings)

        return {
            'total':      total,
            'critical':   critical,
            'high':       high,
            'medium':     medium,
            'low':        low,
            'total_cost': total_cost,
            # Pass full findings so prompt_generator can compute richer stats
            'findings':   self.findings,
        }
