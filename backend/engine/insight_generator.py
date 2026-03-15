import json
import os

class InsightGenerator:
    def __init__(self, templates_path=None):
        if templates_path is None:
            templates_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data', 'insight_templates.json'
            )
        
        with open(templates_path, 'r') as f:
            config = json.load(f)
        
        self.issue_templates = config['issue_templates']
        self.category_impacts = config['category_impacts']
        self.priority_tags = config['priority_tags']
        self.summary_templates = config['summary_templates']

    def generate(self, resource, matched_rules, risk_score, priority):
        if not matched_rules:
            return None
        
        issues = [rule.message for rule in matched_rules]
        suggestions = [rule.suggestion for rule in matched_rules]
        categories = list(set(rule.category for rule in matched_rules))
        
        summary = self._build_summary(resource, categories, issues)
        impact = self._build_impact(issues, categories)
        recommendation = self._build_recommendation(issues, suggestions)
        priority_tag = self.priority_tags.get(priority, "")
        
        return {
            "resource_id": resource.id,
            "resource_type": resource.type,
            "risk_score": risk_score,
            "priority": priority,
            "priority_tag": priority_tag,
            "cost": resource.cost,
            "usage": resource.usage,
            "categories": categories,
            "summary": summary,
            "impact": impact,
            "recommendation": recommendation,
            "issues": issues,
            "suggestions": suggestions,
            "rule_ids": [rule.id for rule in matched_rules]
        }

    def _build_summary(self, resource, categories, issues):
        has_security = 'security' in categories
        has_cost = 'cost' in categories
        has_compliance = 'compliance' in categories
        
        if has_security and has_cost:
            template = self.summary_templates['security_cost']
        elif has_security and has_compliance:
            template = self.summary_templates['compliance_security']
        elif has_security:
            template = self.summary_templates['security_only']
        elif has_cost:
            template = self.summary_templates['cost_only']
        else:
            template = self.summary_templates['general']
        
        return template.format(type=resource.type.capitalize())

    def _build_impact(self, issues, categories):
        impacts = []
        
        for issue in issues:
            if issue in self.issue_templates:
                impact_text = self.issue_templates[issue]['impact']
                if impact_text not in impacts:
                    impacts.append(impact_text)
        
        if not impacts:
            for category in categories:
                if category in self.category_impacts:
                    impacts.append(self.category_impacts[category])
        
        return " | ".join(impacts[:3]) if impacts else "Requires attention"

    def _build_recommendation(self, issues, suggestions):
        recommendations = []
        
        for issue in issues:
            if issue in self.issue_templates:
                fix = self.issue_templates[issue]['fix']
                if fix not in recommendations:
                    recommendations.append(fix)
        
        if not recommendations:
            recommendations = suggestions[:3]
        
        return ". ".join(recommendations[:3]) + "." if recommendations else "Review and remediate."
