"""
llm_connector.py
================
Connects the copilot to Google Gemini (primary) or Claude (fallback).
Falls back gracefully to structured mock responses if no API key is found.

Setup (Gemini - recommended):
    pip install google-generativeai
    Set GEMINI_API_KEY in backend/.env  OR  as environment variable

Setup (Claude - optional fallback):
    pip install anthropic
    Set ANTHROPIC_API_KEY in backend/.env  OR  as environment variable
"""

import os
import json
from dotenv import load_dotenv

# Load .env from the backend folder
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# ── Optional dependency checks ────────────────────────────────────────────────
try:
    import google.generativeai as genai
    _GEMINI_AVAILABLE = True
except ImportError:
    _GEMINI_AVAILABLE = False

try:
    import anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False


# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert Cloud Security & FinOps Copilot embedded in a cloud infrastructure dashboard.

Your job is to analyze cloud resource security findings and give engineers clear, actionable guidance.

ALWAYS structure your responses with these sections (use the exact headers):

**ANALYSIS**
Concise explanation of what is wrong and why it matters.

**RISK IMPACT**
Business and technical consequences if left unresolved.

**RECOMMENDED FIX**
Step-by-step remediation instructions.

**AWS CLI COMMANDS**
Exact AWS CLI commands to fix the issue. Always include these — they are critical.
Format them in a code block like:
```bash
aws <service> <command> --options
```

**ESTIMATED EFFORT**
Time estimate to remediate (e.g., "15 minutes", "1-2 hours").

Keep responses concise and professional. Use real AWS service names and CLI syntax.
Do NOT make up resource IDs or ARNs — use placeholders like <INSTANCE_ID> when the actual value is not known.
"""


class LLMConnector:
    """
    Priority order:
      1. Google Gemini  (GEMINI_API_KEY set + google-generativeai installed)
      2. Claude         (ANTHROPIC_API_KEY set + anthropic installed)
      3. Mock           (structured rule-based fallback)
    """

    def __init__(self):
        gemini_key    = os.environ.get('GEMINI_API_KEY', '').strip()
        anthropic_key = os.environ.get('ANTHROPIC_API_KEY', '').strip()

        if gemini_key and _GEMINI_AVAILABLE:
            self._mode = 'gemini'
            genai.configure(api_key=gemini_key)
            self._gemini_model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=SYSTEM_PROMPT,
            )
            print("[LLM] ✅ Gemini AI connected (model: gemini-1.5-flash)")

        elif anthropic_key and _ANTHROPIC_AVAILABLE:
            self._mode = 'claude'
            self._claude_client = anthropic.Anthropic(api_key=anthropic_key)
            self._claude_model  = 'claude-haiku-4-5-20251001'
            print("[LLM] ✅ Claude AI connected (model: claude-haiku-4-5)")

        else:
            self._mode = 'mock'
            reason = []
            if not gemini_key:    reason.append("no GEMINI_API_KEY")
            if not anthropic_key: reason.append("no ANTHROPIC_API_KEY")
            print(f"[LLM] ⚠️  Mock mode ({', '.join(reason)})")

    # ── Public interface ───────────────────────────────────────────────────────

    def generate_response(self, prompt, query_type, context):
        if self._mode == 'gemini':
            try:
                return self._gemini_response(prompt)
            except Exception as e:
                print(f"[LLM] Gemini error: {e} — falling back to mock")
                return self._mock_response(query_type, context)

        elif self._mode == 'claude':
            try:
                return self._claude_response(prompt)
            except Exception as e:
                print(f"[LLM] Claude error: {e} — falling back to mock")
                return self._mock_response(query_type, context)

        return self._mock_response(query_type, context)

    @property
    def use_mock(self):
        return self._mode == 'mock'

    # ── Gemini API call ────────────────────────────────────────────────────────

    def _gemini_response(self, prompt):
        response = self._gemini_model.generate_content(prompt)
        return response.text

    # ── Claude API call ────────────────────────────────────────────────────────

    def _claude_response(self, prompt):
        message = self._claude_client.messages.create(
            model      = self._claude_model,
            max_tokens = 1024,
            system     = SYSTEM_PROMPT,
            messages   = [{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    # ── Structured mock fallback ───────────────────────────────────────────────

    def _mock_response(self, query_type, context):
        if query_type == 'explain' and context.get('count', 0) > 0:
            return self._mock_explain(context['findings'][0])
        elif query_type == 'fix' and context.get('count', 0) > 0:
            return self._mock_fix(context['findings'][0])
        elif query_type == 'filter':
            return self._mock_filter(context)
        elif query_type == 'summary':
            return self._mock_summary(context)
        elif query_type == 'cost':
            return self._mock_cost(context)
        return ("I can help you analyze cloud security findings.\n\n"
                "Try: 'show critical', 'explain r3', 'fix r3', 'summary', 'show cost issues'")

    def _mock_explain(self, f):
        vuln_line  = f"  - {f.get('vuln_count', 0)} known vulnerabilities ({f.get('cve_count', 0)} CVEs)" if f.get('vuln_count', 0) > 0 else ""
        login_line = f"  - {f.get('failed_logins', 0)} failed login attempts detected" if f.get('failed_logins', 0) > 0 else ""
        ssh_line   = "  - SSH (port 22) exposed to internet" if f.get('ssh_exposed') else ""
        rdp_line   = "  - RDP (port 3389) exposed to internet" if f.get('rdp_exposed') else ""

        security_signals = "\n".join(filter(None, [vuln_line, login_line, ssh_line, rdp_line]))

        return f"""**ANALYSIS**
Resource `{f['resource_id']}` ({f.get('resource_name', f['resource_id'])}) in `{f.get('region', 'unknown')}` is flagged as **{f['priority']}** with a risk score of **{f['risk_score']}**.

Issues detected: {', '.join(f.get('issues', []))}
{f'Security signals:{chr(10)}{security_signals}' if security_signals else ''}
Compliance score: {f.get('compliance_score', 'N/A')}/100

**RISK IMPACT**
{f.get('impact', 'This resource requires immediate attention.')}

Compliance violations: {len(f.get('compliance_violations', []))}
{chr(10).join(f'  - {v}' for v in f.get('compliance_violations', []))}

**RECOMMENDED FIX**
{f.get('recommendation', 'Review and remediate this resource.')}

**AWS CLI COMMANDS**
See the 'fix {f["resource_id"]}' command for specific AWS CLI remediation steps.

**ESTIMATED EFFORT**
{'30-60 minutes' if f['priority'] == 'CRITICAL' else '1-2 hours'} (Priority: {f['priority']})
"""

    def _mock_fix(self, f):
        from copilot.cli_commands import get_all_cli_fixes
        cli_fixes = get_all_cli_fixes(f)

        cli_section = ""
        for issue, commands in cli_fixes.items():
            cli_section += f"\n# Fix: {issue}\n"
            cli_section += "\n".join(commands) + "\n"

        if not cli_section:
            cli_section = f"aws ec2 stop-instances --instance-ids {f['resource_id']}  # example"

        return f"""**ANALYSIS**
Remediation plan for `{f['resource_id']}` ({f.get('resource_name', f['resource_id'])}) — **{f['priority']}** priority.

**RISK IMPACT**
{f.get('impact', 'Unresolved issues increase security and cost exposure.')}
Potential monthly savings if remediated: **${f.get('savings_potential', 0):.2f}**

**RECOMMENDED FIX**
{f.get('recommendation', 'Apply the following fixes.')}

Issues to resolve ({len(f.get('issues', []))}):
{chr(10).join(f'  {i+1}. {issue}' for i, issue in enumerate(f.get('issues', [])))}

**AWS CLI COMMANDS**
```bash
{cli_section.strip()}
```

**ESTIMATED EFFORT**
{'15-30 minutes per issue' if f['priority'] in ['CRITICAL','HIGH'] else '1-2 hours total'}
Rightsizing recommendation: **{f.get('rightsizing', 'review')}**
"""

    def _mock_filter(self, context):
        findings = context.get('findings', [])
        count    = context.get('count', 0)
        if count == 0:
            return "No findings match your criteria."

        lines = [f"**ANALYSIS**\nFound **{count}** resources matching your query.\n"]
        for i, f in enumerate(findings[:6], 1):
            vuln_note  = f" | {f.get('vuln_count',0)} vulns" if f.get('vuln_count', 0) > 0 else ""
            login_note = f" | {f.get('failed_logins',0)} failed logins" if f.get('failed_logins', 0) > 4 else ""
            lines.append(
                f"{i}. `{f['resource_id']}` ({f['resource_type']}) — **{f['priority']}**"
                f"\n   {f['summary']}"
                f"\n   Risk Score: {f['risk_score']} | Cost: ${f['cost']}/mo{vuln_note}{login_note}\n"
            )
        if count > 6:
            lines.append(f"...and **{count - 6}** more resources.\n")

        total_cost    = sum(f['cost'] for f in findings)
        total_savings = sum(f.get('savings_potential', 0) for f in findings)
        lines.append(f"**RISK IMPACT**\nTotal cost at risk: **${total_cost}/month**\nPotential savings: **${total_savings:.2f}/month**")
        return "\n".join(lines)

    def _mock_summary(self, context):
        c = context
        total_savings = sum(f.get('savings_potential', 0) for f in c.get('findings', []))
        total_vulns   = sum(f.get('vuln_count', 0) for f in c.get('findings', []))
        return f"""**ANALYSIS — Executive Summary**

| Priority | Count |
|----------|-------|
| Critical | {c.get('critical', 0)} |
| High     | {c.get('high', 0)} |
| Medium   | {c.get('medium', 0)} |
| Low      | {c.get('low', 0)} |
| **Total**| **{c.get('total', 0)}** |

**RISK IMPACT**
- Monthly cost at risk: **${c.get('total_cost', 0)}/month**
- Potential monthly savings: **${total_savings:.2f}/month**
- Known vulnerabilities across fleet: **{total_vulns}**

**RECOMMENDED FIX**
1. Immediately address **{c.get('critical', 0)} CRITICAL** findings — data breach risk
2. Resolve **{c.get('high', 0)} HIGH** findings within 48 hours
3. Schedule **{c.get('medium', 0)} MEDIUM** findings for next sprint
4. Enable encryption and logging across all unprotected resources

**AWS CLI COMMANDS**
```bash
# Get all SecurityHub findings for account
aws securityhub get-findings --filters '{{"SeverityLabel":[{{"Value":"CRITICAL","Comparison":"EQUALS"}}]}}'

# Enable default EBS encryption across all regions
aws ec2 enable-ebs-encryption-by-default

# List all public S3 buckets
aws s3api list-buckets --query 'Buckets[*].Name' | xargs -I{{}} \\
  aws s3api get-bucket-acl --bucket {{}} 2>/dev/null
```

**ESTIMATED EFFORT**
- Critical fixes: 2-4 hours
- Full remediation: 2-3 sprints
"""

    def _mock_cost(self, context):
        findings       = context.get('findings', [])
        total_savings  = sum(f.get('savings_potential', 0) for f in findings)
        terminate_list = [f for f in findings if f.get('rightsizing') == 'terminate']
        downsize_list  = [f for f in findings if f.get('rightsizing') == 'downsize']

        lines = [
            f"**ANALYSIS — Cost Optimization Report**\n",
            f"Resources to **terminate**: {len(terminate_list)}",
            f"Resources to **downsize**: {len(downsize_list)}",
            f"Total potential savings: **${total_savings:.2f}/month**\n",
        ]
        if terminate_list:
            lines.append("**Top resources to terminate:**")
            for f in terminate_list[:4]:
                lines.append(f"  - `{f['resource_id']}` ({f['resource_type']}) — ${f['cost']}/mo, {f['usage']}% usage")

        lines.append(f"""
**AWS CLI COMMANDS**
```bash
# Stop all idle EC2 instances (review list first)
aws ec2 describe-instances \\
  --filters Name=instance-state-name,Values=running \\
  --query 'Reservations[].Instances[?CpuOptions.CoreCount<=`1`].[InstanceId]'

# Get Cost Explorer rightsizing recommendations
aws ce get-rightsizing-recommendation --service EC2

# List unused EBS volumes
aws ec2 describe-volumes \\
  --filters Name=status,Values=available \\
  --query 'Volumes[*].[VolumeId,Size,CreateTime]'
```""")
        return "\n".join(lines)
