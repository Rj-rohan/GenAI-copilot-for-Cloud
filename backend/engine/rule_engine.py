import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.rule_loader import RuleLoader
from engine.rule_evaluator import RuleEvaluator
from engine.risk_scorer import RiskScorer
from engine.insight_generator import InsightGenerator

class RuleEngine:
    def __init__(self, rules_path, provider='aws'):
        self.provider = provider
        self.rule_loader = RuleLoader(rules_path)
        self.rule_evaluator = RuleEvaluator()
        self.risk_scorer = RiskScorer()
        self.insight_generator = InsightGenerator(provider=provider)
        self.rules = self.rule_loader.load()

    def analyze(self, resources):
        findings = []
        
        for resource in resources:
            matched_rules = self.rule_evaluator.evaluate(resource, self.rules)
            
            if matched_rules:
                risk_score, score_breakdown = self.risk_scorer.calculate_score(resource, matched_rules)
                priority = self.risk_scorer.calculate_priority(risk_score)

                insight = self.insight_generator.generate(
                    resource, matched_rules, risk_score, priority, score_breakdown
                )
                
                if insight:
                    findings.append(insight)
        
        return findings

    def save_findings(self, findings, output_path):
        with open(output_path, 'w') as f:
            json.dump(findings, f, indent=2)
