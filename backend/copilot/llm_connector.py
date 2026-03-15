class LLMConnector:
    def __init__(self, use_mock=True):
        self.use_mock = use_mock
        # In production, initialize OpenAI/Bedrock client here
        # self.client = openai.Client(api_key=...)

    def generate_response(self, prompt, query_type, context):
        if self.use_mock:
            return self._mock_response(query_type, context)
        else:
            # In production, call actual LLM
            # return self.client.chat.completions.create(...)
            return self._mock_response(query_type, context)

    def _mock_response(self, query_type, context):
        """Rule-based intelligent responses for demo"""
        
        if query_type == 'explain' and context['count'] > 0:
            finding = context['findings'][0]
            return self._explain_finding(finding)
        
        elif query_type == 'fix' and context['count'] > 0:
            finding = context['findings'][0]
            return self._fix_recommendation(finding)
        
        elif query_type == 'filter':
            return self._filter_summary(context)
        
        elif query_type == 'summary':
            return self._executive_summary(context)
        
        return "I can help you analyze cloud security findings. Try commands like 'show high risk', 'explain r3', or 'summary'."

    def _explain_finding(self, finding):
        priority_emoji = finding.get('priority_tag', '')
        
        response = f"""{priority_emoji} RISK ANALYSIS

Resource: {finding['resource_id']} ({finding['resource_type'].upper()})
Risk Score: {finding['risk_score']} | Priority: {finding['priority']}

WHY THIS IS CRITICAL:
{finding['summary']}

POTENTIAL IMPACT:
{finding['impact']}

BUSINESS RISK:
"""
        if finding['priority'] == 'CRITICAL':
            response += "This resource poses an immediate security threat and could lead to data breaches, compliance violations, or significant financial loss."
        elif finding['priority'] == 'HIGH':
            response += "This resource has serious vulnerabilities that should be addressed urgently to prevent security incidents."
        else:
            response += "While not immediately critical, this issue should be addressed to maintain security posture and optimize costs."
        
        response += f"\n\nCOST IMPACT: ${finding['cost']}/month at risk"
        
        return response

    def _fix_recommendation(self, finding):
        response = f"""REMEDIATION PLAN

Resource: {finding['resource_id']} ({finding['resource_type'].upper()})
Priority: {finding['priority']}

RECOMMENDED ACTIONS:
{finding['recommendation']}

STEP-BY-STEP GUIDE:
"""
        
        steps = finding['recommendation'].split('. ')
        for i, step in enumerate(steps, 1):
            if step.strip():
                response += f"\n{i}. {step.strip()}"
        
        response += f"\n\nESTIMATED TIME: 15-30 minutes"
        response += f"\nCOST SAVINGS: ${finding['cost']}/month"
        
        return response

    def _filter_summary(self, context):
        findings = context['findings']
        count = context['count']
        
        if count == 0:
            return "No findings match your criteria."
        
        response = f"FILTERED RESULTS: {count} resources found\n\n"
        
        for i, f in enumerate(findings[:5], 1):
            response += f"{i}. {f['priority_tag']} {f['resource_id']} ({f['resource_type']})\n"
            response += f"   {f['summary']}\n"
            response += f"   Risk Score: {f['risk_score']} | Cost: ${f['cost']}\n\n"
        
        if count > 5:
            response += f"... and {count - 5} more resources\n"
        
        total_cost = sum(f['cost'] for f in findings)
        response += f"\nTotal Cost at Risk: ${total_cost}/month"
        
        return response

    def _executive_summary(self, context):
        return f"""EXECUTIVE SUMMARY REPORT

OVERVIEW:
Total Resources with Issues: {context['total']}
- Critical Priority: {context['critical']}
- High Priority: {context['high']}
- Medium Priority: {context['medium']}
- Low Priority: {context['low']}

FINANCIAL IMPACT:
Total Monthly Cost at Risk: ${context['total_cost']}

KEY RECOMMENDATIONS:
1. Address {context['critical']} critical security issues immediately
2. Review and remediate {context['high']} high-priority vulnerabilities
3. Implement cost optimization for idle resources
4. Enable encryption and logging across all resources

NEXT STEPS:
- Prioritize critical findings for immediate action
- Schedule remediation for high-priority items within 48 hours
- Plan cost optimization initiatives for medium/low priority items
"""
