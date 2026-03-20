class RuleEvaluator:
    def evaluate(self, resource, rules):
        matched_rules = []
        
        for rule in rules:
            if self._check_condition(resource, rule):
                matched_rules.append(rule)
        
        return matched_rules

    def _check_condition(self, resource, rule):
        if rule.condition:
            if not self._evaluate_condition(resource, rule.condition):
                return False
        
        return self._evaluate_condition(resource, {
            'field': rule.field,
            'operator': rule.operator,
            'value': rule.value
        })

    def _evaluate_condition(self, resource, condition):
        field_value = getattr(resource, condition['field'], None)
        operator = condition['operator']
        expected_value = condition['value']
        
        if operator == 'equals':
            return field_value == expected_value
        elif operator == 'less':
            return field_value < expected_value
        elif operator == 'greater':
            return field_value > expected_value
        elif operator == 'less_equal':
            return field_value <= expected_value
        elif operator == 'greater_equal':
            return field_value >= expected_value
        
        return False
