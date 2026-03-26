"""
prompt_generator.py
===================
Builds rich, context-aware prompts for Claude/Gemini that include all data from
all 5 collection sources plus explicit instructions to return cloud-specific CLI commands.
Supports AWS, Azure, and GCP.
"""

import json

# Cloud provider service name mappings
CLOUD_SERVICES = {
    'aws': {
        'activity': 'CloudTrail',
        'security': 'SecurityHub',
        'cost': 'Cost Explorer',
        'config': 'AWS Config',
        'metrics': 'CloudWatch'
    },
    'azure': {
        'activity': 'Activity Log',
        'security': 'Security Center',
        'cost': 'Cost Management',
        'config': 'Resource Graph',
        'metrics': 'Azure Monitor'
    },
    'gcp': {
        'activity': 'Cloud Audit Logs',
        'security': 'Security Command Center',
        'cost': 'Cloud Billing',
        'config': 'Asset Inventory',
        'metrics': 'Cloud Monitoring'
    }
}

CLI_NAMES = {
    'aws': 'AWS CLI',
    'azure': 'Azure CLI',
    'gcp': 'gcloud CLI'
}


class PromptGenerator:
    def __init__(self, provider='aws'):
        self.provider = provider
        self.services = CLOUD_SERVICES.get(provider, CLOUD_SERVICES['aws'])
        self.cli_name = CLI_NAMES.get(provider, 'CLI')

    # ── Prompt builders ───────────────────────────────────────────────────────

    def generate_prompt(self, query_type, context):
        if query_type == 'explain' and context.get('count', 0) > 0:
            return self._explain_prompt(context['findings'][0])

        elif query_type == 'fix' and context.get('count', 0) > 0:
            return self._fix_prompt(context['findings'][0])

        elif query_type == 'filter':
            return self._filter_prompt(context)

        elif query_type == 'summary':
            return self._summary_prompt(context)

        elif query_type == 'cost':
            return self._cost_prompt(context)

        return (
            f"The user asked: \"{context.get('original_query', 'general question')}\"\n\n"
            f"Available findings summary:\n{self._mini_stats(context)}\n\n"
            "Provide helpful cloud security guidance based on their question."
        )

    # ── Individual prompt templates ───────────────────────────────────────────

    def _explain_prompt(self, f):
        from copilot.cli_commands_multicloud import get_all_cli_fixes
        cli_fixes = get_all_cli_fixes(f, self.provider)
        cli_block = self._format_cli_block(cli_fixes)

        return f"""A cloud engineer is asking about a specific resource. Explain the risks clearly.

CLOUD PROVIDER: {self.provider.upper()}

RESOURCE DETAILS (from 5 data sources):
  Resource ID   : {f['resource_id']}
  Name          : {f.get('resource_name', f['resource_id'])}
  Type          : {f['resource_type']}
  Region        : {f.get('region', 'unknown')}
  Priority      : {f['priority']}
  Risk Score    : {f['risk_score']}

SECURITY SIGNALS (from {self.services['security']} + {self.services['activity']}):
  Vulnerabilities   : {f.get('vuln_count', 0)} ({f.get('cve_count', 0)} CVEs)
  Failed Logins     : {f.get('failed_logins', 0)} (last 30 days)
  Suspicious APIs   : {f.get('suspicious_api_calls', 0)}
  Open Ports        : {f.get('open_ports', [])}
  SSH Exposed       : {f.get('ssh_exposed', False)}
  RDP Exposed       : {f.get('rdp_exposed', False)}
  Compliance Score  : {f.get('compliance_score', 100)}/100

COST SIGNALS (from {self.services['cost']}):
  Monthly Cost      : ${f.get('cost', 0)}/month
  Cost Trend        : {f.get('cost_trend_pct', 0):+.1f}%
  Savings Potential : ${f.get('savings_potential', 0):.2f}/month
  Rightsizing       : {f.get('rightsizing', 'none')}
  Last Activity     : {f.get('last_activity_days', 0)} days ago

COMPLIANCE (from {self.services['config']}):
  Violations        : {json.dumps(f.get('compliance_violations', []))}
  Has Tags          : {f.get('has_tags', True)}

ISSUES DETECTED ({len(f.get('issues', []))} total):
{chr(10).join(f'  - {i}' for i in f.get('issues', []))}

AVAILABLE {self.cli_name} FIXES (pre-computed):
{cli_block}

Provide a detailed explanation of why this resource is risky and how to fix it.
Include the {self.cli_name} commands above in your response, formatted as a bash code block.
"""

    def _fix_prompt(self, f):
        from copilot.cli_commands_multicloud import get_all_cli_fixes
        cli_fixes = get_all_cli_fixes(f, self.provider)
        cli_block = self._format_cli_block(cli_fixes)

        return f"""A cloud engineer wants to fix this resource. Provide a complete remediation plan.

CLOUD PROVIDER: {self.provider.upper()}

RESOURCE TO FIX:
  ID            : {f['resource_id']}
  Name          : {f.get('resource_name', f['resource_id'])}
  Type          : {f['resource_type']}
  Region        : {f.get('region', 'unknown')}
  Priority      : {f['priority']}
  Risk Score    : {f['risk_score']}

ISSUES TO RESOLVE ({len(f.get('issues', []))} issues):
{chr(10).join(f'  {i+1}. {issue}' for i, issue in enumerate(f.get('issues', [])))}

SECURITY STATE:
  Vulnerabilities   : {f.get('vuln_count', 0)} ({f.get('cve_count', 0)} CVEs)
  Failed Logins     : {f.get('failed_logins', 0)}
  Open Ports        : {f.get('open_ports', [])}
  SSH Exposed       : {f.get('ssh_exposed', False)}
  RDP Exposed       : {f.get('rdp_exposed', False)}
  Compliance Score  : {f.get('compliance_score', 100)}/100
  Compliance Violations: {f.get('compliance_violation_count', 0)}

COST STATE:
  Monthly Cost      : ${f.get('cost', 0)}/month
  Savings Potential : ${f.get('savings_potential', 0):.2f}/month
  Rightsizing       : {f.get('rightsizing', 'none')}

PRE-COMPUTED {self.cli_name} COMMANDS:
{cli_block}

Generate a step-by-step remediation plan.
IMPORTANT: Include all relevant {self.cli_name} commands from above in a bash code block.
Group commands by issue. Estimate time for each step.
"""

    def _filter_prompt(self, context):
        findings = context.get('findings', [])
        count    = context.get('count', 0)
        filters  = context.get('filters_applied', {})

        findings_text = ""
        for f in findings[:8]:
            findings_text += (
                f"  - {f['resource_id']} ({f['resource_type']}) [{f['priority']}]"
                f" Score:{f['risk_score']} Cost:${f['cost']}/mo"
                f" Vulns:{f.get('vuln_count', 0)} Logins:{f.get('failed_logins', 0)}"
                f" | {f['summary']}\n"
            )

        total_cost    = sum(f['cost'] for f in findings)
        total_savings = sum(f.get('savings_potential', 0) for f in findings)
        total_vulns   = sum(f.get('vuln_count', 0) for f in findings)

        return f"""A cloud engineer filtered findings. Summarize and highlight key risks.

CLOUD PROVIDER: {self.provider.upper()}
FILTER APPLIED: {json.dumps(filters)}
TOTAL MATCHING: {count} resources

FINDINGS (showing up to 8):
{findings_text}
AGGREGATE STATS:
  Total Cost at Risk : ${total_cost}/month
  Potential Savings  : ${total_savings:.2f}/month
  Total Vulnerabilities: {total_vulns}
  Critical Count     : {sum(1 for f in findings if f['priority'] == 'CRITICAL')}

Summarize what is found. Highlight the top 3 most critical items.
Include at least one relevant {self.cli_name} command for the most common issue in this filtered set.
"""

    def _summary_prompt(self, context):
        findings      = context.get('findings', [])
        total_savings = sum(f.get('savings_potential', 0) for f in findings)
        total_vulns   = sum(f.get('vuln_count', 0) for f in findings)
        total_logins  = sum(f.get('failed_logins', 0) for f in findings)
        ssh_count     = sum(1 for f in findings if f.get('ssh_exposed'))
        rdp_count     = sum(1 for f in findings if f.get('rdp_exposed'))

        top3 = sorted(findings, key=lambda x: x['risk_score'], reverse=True)[:3]
        top3_text = "\n".join(
            f"  {i+1}. {f['resource_id']} ({f.get('resource_name','')}) — Score:{f['risk_score']} — {f['summary']}"
            for i, f in enumerate(top3)
        )

        return f"""Generate a C-suite executive summary of the cloud security and cost posture.

CLOUD PROVIDER: {self.provider.upper()}

FLEET OVERVIEW:
  Total Issues  : {context.get('total', 0)}
  Critical      : {context.get('critical', 0)}
  High          : {context.get('high', 0)}
  Medium        : {context.get('medium', 0)}
  Low           : {context.get('low', 0)}

FINANCIAL IMPACT:
  Total Cost at Risk    : ${context.get('total_cost', 0)}/month
  Potential Savings     : ${total_savings:.2f}/month

SECURITY SIGNALS:
  Total Vulnerabilities : {total_vulns}
  Total Failed Logins   : {total_logins}
  SSH Internet-Exposed  : {ssh_count} resources
  RDP Internet-Exposed  : {rdp_count} resources

TOP 3 HIGHEST RISK RESOURCES:
{top3_text}

Write a professional executive summary covering:
1. Current security posture
2. Top 3 risks that need immediate action
3. Financial exposure and savings opportunity
4. Recommended 30-day remediation roadmap
5. Key {self.cli_name} commands for the most urgent fixes
"""

    def _cost_prompt(self, context):
        findings      = context.get('findings', [])
        total_savings = sum(f.get('savings_potential', 0) for f in findings)
        terminate     = [f for f in findings if f.get('rightsizing') == 'terminate']
        downsize      = [f for f in findings if f.get('rightsizing') == 'downsize']

        idle_text = "\n".join(
            f"  - {f['resource_id']} ({f.get('resource_name','')}) {f['resource_type']}"
            f" | Usage:{f['usage']}% | Cost:${f['cost']}/mo | Savings:${f.get('savings_potential',0):.2f}"
            for f in (terminate + downsize)[:8]
        )

        return f"""Generate a FinOps cost optimization report for this cloud environment.

CLOUD PROVIDER: {self.provider.upper()}

COST SUMMARY:
  Total Resources with Issues : {context.get('total', 0)}
  Total Cost at Risk          : ${context.get('total_cost', 0)}/month
  Potential Monthly Savings   : ${total_savings:.2f}/month

RIGHTSIZING BREAKDOWN:
  Resources to TERMINATE : {len(terminate)}
  Resources to DOWNSIZE  : {len(downsize)}

IDLE/UNDERUTILIZED RESOURCES:
{idle_text if idle_text else '  None identified'}

Provide a detailed cost optimization plan with:
1. Prioritized list of resources to terminate vs downsize
2. Expected monthly savings
3. {self.cli_name} commands to stop/terminate/resize the top 5 resources
4. Recommendations for Reserved Instances or Savings Plans
"""

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _format_cli_block(self, cli_fixes):
        if not cli_fixes:
            return "  (No specific CLI commands pre-computed for this resource)"
        lines = []
        for issue, commands in cli_fixes.items():
            lines.append(f"  # {issue}")
            for cmd in commands:
                lines.append(f"  {cmd}")
            lines.append("")
        return "\n".join(lines)

    def _mini_stats(self, context):
        return (
            f"  Total: {context.get('total', '?')} | "
            f"Critical: {context.get('critical', '?')} | "
            f"High: {context.get('high', '?')} | "
            f"Cost at Risk: ${context.get('total_cost', '?')}/month"
        )
