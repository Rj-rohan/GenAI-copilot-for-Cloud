import os
import sys
import json
import argparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from collector.collector_orchestrator import CollectorOrchestrator
from engine.rule_engine import RuleEngine


def main():
    parser = argparse.ArgumentParser(description='Cloud Security Analysis Pipeline')
    parser.add_argument('--provider', '-p', choices=['aws', 'azure', 'gcp'], 
                        default='aws', help='Cloud provider (default: aws)')
    args = parser.parse_args()
    
    provider = args.provider
    base_path      = os.path.dirname(os.path.abspath(__file__))
    sources_path   = os.path.join(base_path, 'data', 'sources')
    inventory_path = os.path.join(base_path, 'data', f'resources_{provider}.json')
    
    # Fallback to default if provider-specific file doesn't exist
    if not os.path.exists(inventory_path):
        inventory_path = os.path.join(base_path, 'data', 'resources.json')
    
    rules_path     = os.path.join(base_path, 'data', 'rules.json')
    output_path    = os.path.join(base_path, 'data', f'findings_{provider}.json')
    frontend_path  = os.path.join(base_path, '..', 'frontend', 'public', 'findings.json')

    # Load cloud provider config
    config_path = os.path.join(base_path, 'data', 'cloud_providers.json')
    with open(config_path, 'r') as f:
        cloud_config = json.load(f)
    
    provider_info = cloud_config['providers'][provider]

    print("=" * 60)
    print(f"  GenAI Cloud Security Copilot")
    print(f"  Provider: {provider_info['name']} ({provider.upper()})")
    print("=" * 60)

    # ── Step 1: Data Collection Layer ─────────────────────────────
    print("\n[1] Data Collection Layer")
    print("-" * 40)
    print(f"  Cloud Provider: {provider_info['name']}")
    print(f"  Services:")
    for service_type, service_name in provider_info['services'].items():
        print(f"    - {service_name}")
    
    orchestrator = CollectorOrchestrator(sources_path, inventory_path, provider)
    resources    = orchestrator.collect()

    # ── Step 2: Rule Engine ────────────────────────────────────────
    print("\n[2] Analyzer Engine - Rule Engine")
    print("-" * 40)
    engine = RuleEngine(rules_path, provider)
    print(f"    Loaded {len(engine.rules)} rules")

    # ── Step 3: Risk Analysis ──────────────────────────────────────
    print("\n[3] Risk Analysis")
    print("-" * 40)
    findings = engine.analyze(resources)
    print(f"    Analyzed {len(resources)} resources -> {len(findings)} findings")

    # ── Step 4: Save Findings ──────────────────────────────────────
    print("\n[4] Saving Findings")
    print("-" * 40)
    engine.save_findings(findings, output_path)
    print(f"    [OK] Backend:  {output_path}")

    try:
        engine.save_findings(findings, frontend_path)
        print(f"    [OK] Frontend: {frontend_path}")
    except Exception:
        print(f"    [WARN] Could not write to frontend path")

    # ── Step 5: Summary ───────────────────────────────────────────
    print("\n[5] Summary")
    print("-" * 40)
    critical = sum(1 for f in findings if f['priority'] == 'CRITICAL')
    high     = sum(1 for f in findings if f['priority'] == 'HIGH')
    medium   = sum(1 for f in findings if f['priority'] == 'MEDIUM')
    low      = sum(1 for f in findings if f['priority'] == 'LOW')

    print(f"    [CRITICAL] : {critical}")
    print(f"    [HIGH]     : {high}")
    print(f"    [MEDIUM]   : {medium}")
    print(f"    [LOW]      : {low}")
    print(f"    [TOTAL]    : {len(findings)}")

    total_cost     = sum(f['cost'] for f in findings)
    total_savings  = sum(f.get('savings_potential', 0) for f in findings)
    total_vulns    = sum(f.get('vuln_count', 0) for f in findings)
    total_failed   = sum(f.get('failed_logins', 0) for f in findings)

    print(f"\n    Total Cost at Risk     : ${total_cost}/month")
    print(f"    Potential Savings      : ${total_savings:.2f}/month")
    print(f"    Total Vulnerabilities  : {total_vulns}")
    print(f"    Total Failed Logins    : {total_failed}")

    # ── Step 6: Top Critical Findings ─────────────────────────────
    print("\n[6] Top 3 Critical Findings")
    print("-" * 40)
    sorted_findings = sorted(findings, key=lambda x: x['risk_score'], reverse=True)
    for f in sorted_findings[:3]:
        print(f"\n    Resource : {f['resource_id']} ({f['resource_name']})")
        print(f"    Region   : {f['region']}")
        print(f"    Provider : {provider.upper()}")
        print(f"    Score    : {f['risk_score']} | Priority: {f['priority']}")
        print(f"    Issues   : {len(f['issues'])} detected")
        print(f"    Impact   : {f['impact'][:80]}...")


if __name__ == "__main__":
    main()
