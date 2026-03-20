import json
import os

class RiskScorer:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data', 'scoring_config.json'
            )
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        self.category_weights = config['category_weights']
        self.thresholds = config['priority_thresholds']
        self.factors = config['factors']

    def calculate_score(self, resource, matched_rules):
        base_score = self._calculate_weighted_score(matched_rules)
        cost_factor = self._calculate_cost_factor(resource.cost)
        usage_factor = self._calculate_usage_factor(resource.usage)
        
        total_score = base_score + cost_factor + usage_factor
        
        exposure_multiplier = self._calculate_exposure_multiplier(resource)
        final_score = total_score * exposure_multiplier
        
        return round(final_score, 2)

    def _calculate_weighted_score(self, matched_rules):
        score = 0
        for rule in matched_rules:
            weight = self.category_weights.get(rule.category, 1)
            score += rule.risk * weight
        return score

    def _calculate_cost_factor(self, cost):
        return cost / self.factors['cost_divisor']

    def _calculate_usage_factor(self, usage):
        if usage < self.factors['usage_threshold']:
            return self.factors['usage_penalty']
        return 0

    def _calculate_exposure_multiplier(self, resource):
        if resource.public:
            return self.factors['exposure_multiplier']
        return 1.0

    def calculate_priority(self, risk_score):
        if risk_score >= self.thresholds['critical']:
            return "CRITICAL"
        elif risk_score >= self.thresholds['high']:
            return "HIGH"
        elif risk_score >= self.thresholds['medium']:
            return "MEDIUM"
        else:
            return "LOW"
