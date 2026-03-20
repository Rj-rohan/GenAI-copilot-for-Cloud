import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser.data_parser import DataParser
from engine.rule_engine import RuleEngine

def main():
    base_path = os.path.dirname(os.path.dirname(__file__))
    findings_path = os.path.join(base_path, 'data', 'findings.json')
    
    with open(findings_path, 'r', encoding='utf-8') as f:
        findings = json.load(f)
    
    print("=" * 80)
    print("INSIGHT GENERATOR - ACTIONABLE INTELLIGENCE REPORT")
    print("=" * 80)
    
    print("\n[INSIGHT ENGINE FEATURES]")
    print("  - Template-based message generation")
    print("  - Context-aware impact analysis")
    print("  - Prioritized recommendations")
    print("  - Human-readable summaries")
    print("  - Visual priority tags")
    
    print("\n" + "=" * 80)
    print("CRITICAL INSIGHTS (Top 3)")
    print("=" * 80)
    
    critical = [f for f in findings if f['priority'] == 'CRITICAL']
    
    for i, finding in enumerate(critical[:3], 1):
        print(f"\n{finding['priority_tag']} FINDING #{i}")
        print(f"Resource: {finding['resource_id']} ({finding['resource_type'].upper()})")
        print(f"Risk Score: {finding['risk_score']}")
        print(f"\nSummary:")
        print(f"  {finding['summary']}")
        print(f"\nImpact:")
        print(f"  {finding['impact']}")
        print(f"\nRecommendation:")
        print(f"  {finding['recommendation']}")
        print(f"\nCost Impact: ${finding['cost']}/month")
        print("-" * 80)
    
    print("\n" + "=" * 80)
    print("INSIGHT BREAKDOWN BY CATEGORY")
    print("=" * 80)
    
    security_issues = [f for f in findings if 'security' in f['categories']]
    cost_issues = [f for f in findings if 'cost' in f['categories']]
    compliance_issues = [f for f in findings if 'compliance' in f['categories']]
    
    print(f"\nSecurity Issues: {len(security_issues)}")
    print(f"Cost Optimization: {len(cost_issues)}")
    print(f"Compliance Violations: {len(compliance_issues)}")
    
    print("\n" + "=" * 80)
    print("ACTIONABLE RECOMMENDATIONS SUMMARY")
    print("=" * 80)
    
    all_recommendations = []
    for f in findings:
        rec = f['recommendation']
        if rec not in all_recommendations:
            all_recommendations.append(rec)
    
    print(f"\nTotal Unique Recommendations: {len(all_recommendations)}")
    print("\nTop 5 Most Critical Actions:")
    
    critical_recs = []
    for f in critical[:5]:
        if f['recommendation'] not in critical_recs:
            critical_recs.append(f['recommendation'])
    
    for i, rec in enumerate(critical_recs[:5], 1):
        print(f"  {i}. {rec}")
    
    print("\n" + "=" * 80)
    print("EXECUTIVE SUMMARY")
    print("=" * 80)
    
    total_cost = sum(f['cost'] for f in findings)
    critical_cost = sum(f['cost'] for f in critical)
    
    print(f"\nTotal Resources with Issues: {len(findings)}")
    print(f"Critical Priority: {len(critical)}")
    print(f"Total Monthly Cost at Risk: ${total_cost}")
    print(f"Critical Cost Exposure: ${critical_cost}")
    
    print("\nKey Insights:")
    print(f"  - {len([f for f in critical if 'storage' in f['resource_type']])} public storage buckets detected")
    print(f"  - {len([f for f in findings if 'Encryption disabled' in f['issues']])} resources without encryption")
    print(f"  - {len([f for f in findings if 'Unused resource' in f['issues']])} unused resources wasting budget")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
