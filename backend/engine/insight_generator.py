import json
import os
import sys

# Allow importing from sibling packages (copilot/)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from copilot.cli_commands import get_all_cli_fixes
    _HAS_CLI = True
except ImportError:
    _HAS_CLI = False


class InsightGenerator:
    def __init__(self, templates_path=None):
        if templates_path is None:
            templates_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data', 'insight_templates.json'
            )

        with open(templates_path, 'r') as f:
            config = json.load(f)

        self.issue_templates   = config['issue_templates']
        self.category_impacts  = config['category_impacts']
        self.priority_tags     = config['priority_tags']
        self.summary_templates = config['summary_templates']

    def generate(self, resource, matched_rules, risk_score, priority, score_breakdown=None):
        if not matched_rules:
            return None

        issues      = [rule.message for rule in matched_rules]
        suggestions = [rule.suggestion for rule in matched_rules]
        categories  = list(set(rule.category for rule in matched_rules))

        summary        = self._build_summary(resource, categories, issues)
        impact         = self._build_impact(issues, categories)
        recommendation = self._build_recommendation(issues, suggestions)
        priority_tag   = self.priority_tags.get(priority, "")

        # Build a partial finding dict so cli_commands can resolve placeholders
        partial = {
            'issues':        issues,
            'resource_type': resource.type,
            'resource_id':   resource.id,
            'resource_name': resource.resource_name,
            'region':        resource.region,
        }
        cli_fixes = get_all_cli_fixes(partial) if _HAS_CLI else {}

        return {
            # Core identifiers
            "resource_id":   resource.id,
            "resource_name": resource.resource_name,
            "resource_type": resource.type,
            "region":        resource.region,

            # Risk assessment
            "risk_score":   risk_score,
            "priority":     priority,
            "priority_tag": priority_tag,
            "categories":   categories,
            "rule_ids":     [rule.id for rule in matched_rules],

            # Human-readable insights
            "summary":        summary,
            "impact":         impact,
            "recommendation": recommendation,
            "issues":         issues,
            "suggestions":    suggestions,

            # AWS CLI / boto3 fix commands keyed by issue
            "cli_fixes": cli_fixes,

            # Risk score breakdown (for transparency / demo)
            "score_breakdown": score_breakdown or {},

            # Base metrics (Cost Explorer + inventory)
            "cost":             resource.cost,
            "usage":            resource.usage,
            "savings_potential": resource.savings_potential,
            "cost_trend_pct":   resource.cost_trend_pct,
            "rightsizing":      resource.rightsizing,

            # Security signals (SecurityHub)
            "vuln_count":       resource.vuln_count,
            "cve_count":        resource.cve_count,
            "compliance_score": resource.compliance_score,
            "open_ports":       resource.open_ports,
            "ssh_exposed":      resource.ssh_exposed,
            "rdp_exposed":      resource.rdp_exposed,

            # Activity signals (CloudTrail)
            "failed_logins":        resource.failed_logins,
            "suspicious_api_calls": resource.suspicious_api_calls,
            "last_activity_days":   resource.last_activity_days,

            # Performance metrics (CloudWatch)
            "cpu_avg":          resource.cpu_avg,
            "memory_avg":       resource.memory_avg,
            "disk_utilization": resource.disk_utilization,

            # Compliance (Config)
            "compliance_violations":      resource.compliance_violations,
            "compliance_violation_count": resource.compliance_violation_count,
            "has_tags":                   resource.has_tags,
            "tags":                       resource.tags
        }

    def _build_summary(self, resource, categories, issues):
        has_security   = 'security' in categories
        has_cost       = 'cost' in categories
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
