class QueryHandler:
    def __init__(self):
        self.query_patterns = {
            'filter': ['show', 'list', 'display', 'get'],
            'explain': ['why', 'explain', 'what', 'how come'],
            'fix': ['fix', 'resolve', 'remediate', 'solve'],
            'summary': ['summary', 'report', 'overview', 'total'],
            'cost': ['cost', 'expense', 'spending', 'waste']
        }
        
        self.priority_keywords = ['critical', 'high', 'medium', 'low']
        self.category_keywords = ['security', 'cost', 'compliance']
        self.resource_keywords = ['compute', 'storage', 'database', 'network']

    def parse_query(self, query):
        query_lower = query.lower()
        
        query_type = self._detect_query_type(query_lower)
        filters = self._extract_filters(query_lower)
        resource_id = self._extract_resource_id(query_lower)
        
        return {
            'type': query_type,
            'filters': filters,
            'resource_id': resource_id,
            'original': query
        }

    def _detect_query_type(self, query):
        for qtype, keywords in self.query_patterns.items():
            if any(keyword in query for keyword in keywords):
                return qtype
        return 'general'

    def _extract_filters(self, query):
        filters = {}
        
        for priority in self.priority_keywords:
            if priority in query:
                filters['priority'] = priority.upper()
        
        for category in self.category_keywords:
            if category in query:
                filters['category'] = category
        
        for resource_type in self.resource_keywords:
            if resource_type in query:
                filters['resource_type'] = resource_type
        
        return filters

    def _extract_resource_id(self, query):
        import re
        match = re.search(r'\br\d+\b', query)
        return match.group(0) if match else None
