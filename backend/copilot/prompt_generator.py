class PromptGenerator:
    def __init__(self):
        self.system_prompt = """You are a Cloud Security Copilot, an expert advisor for cloud infrastructure security and cost optimization.
Your role is to analyze cloud resource findings and provide clear, actionable insights.
Be concise, professional, and focus on practical recommendations."""

        self.templates = {
            'explain': """Analyze this cloud resource finding and explain the risks:

Resource: {resource_id} ({resource_type})
Priority: {priority}
Risk Score: {risk_score}
Summary: {summary}
Impact: {impact}

Provide a clear explanation of why this is a concern and what could happen if not addressed.""",

            'fix': """Provide step-by-step remediation guidance for this finding:

Resource: {resource_id} ({resource_type})
Priority: {priority}
Issues: {issues}
Current Recommendation: {recommendation}

Give detailed, actionable steps to fix these issues.""",

            'filter': """Summarize these filtered cloud resource findings:

Total Findings: {count}
Filters Applied: {filters}

Findings:
{findings_summary}

Provide a brief overview and highlight the most critical items.""",

            'summary': """Generate an executive summary report:

Total Resources with Issues: {total}
Critical: {critical}
High: {high}
Medium: {medium}
Low: {low}
Total Cost at Risk: ${total_cost}

Provide key insights and top recommendations."""
        }

    def generate_prompt(self, query_type, context):
        if query_type == 'explain' and context['count'] > 0:
            finding = context['findings'][0]
            return self.templates['explain'].format(
                resource_id=finding['resource_id'],
                resource_type=finding['resource_type'],
                priority=finding['priority'],
                risk_score=finding['risk_score'],
                summary=finding['summary'],
                impact=finding['impact']
            )
        
        elif query_type == 'fix' and context['count'] > 0:
            finding = context['findings'][0]
            return self.templates['fix'].format(
                resource_id=finding['resource_id'],
                resource_type=finding['resource_type'],
                priority=finding['priority'],
                issues=', '.join(finding['issues']),
                recommendation=finding['recommendation']
            )
        
        elif query_type == 'filter':
            findings_summary = self._format_findings_summary(context['findings'][:5])
            return self.templates['filter'].format(
                count=context['count'],
                filters=context.get('filters_applied', {}),
                findings_summary=findings_summary
            )
        
        elif query_type == 'summary':
            return self.templates['summary'].format(**context)
        
        return f"Analyze these cloud security findings and provide insights: {context}"

    def _format_findings_summary(self, findings):
        summary = []
        for f in findings:
            summary.append(f"- {f['resource_id']} ({f['resource_type']}): {f['summary']} [Priority: {f['priority']}]")
        return '\n'.join(summary)
