import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser.data_parser import DataParser
from engine.rule_engine import RuleEngine

def main():
    base_path = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(base_path, 'data', 'resources.json')
    rules_path = os.path.join(base_path, 'data', 'rules.json')
    
    print("=" * 70)
    print("WEIGHTED RISK SCORING ENGINE - DETAILED ANALYSIS")
    print("=" * 70)
    
    parser = DataParser(data_path)
    resources = parser.parse()
    
    engine = RuleEngine(rules_path)
    findings = engine.analyze(resources)
    
    print("\n[SCORING FORMULA]")
    print("  Base Score = SUM(rule_risk × category_weight)")
    print("  Cost Factor = cost / 5")
    print("  Usage Factor = 5 (if usage < 5)")
    print("  Exposure Multiplier = 1.5 (if public)")
    print("  Final Score = (Base + Cost + Usage) × Exposure")
    
    print("\n[CATEGORY WEIGHTS]")
    print("  Security: 4x | Compliance: 3x | Cost: 2x")
    
    print("\n[PRIORITY THRESHOLDS]")
    print("  CRITICAL: >=100 | HIGH: >=60 | MEDIUM: >=30 | LOW: <30")
    
    print("\n" + "=" * 70)
    print("TOP 5 CRITICAL/HIGH RISK RESOURCES")
    print("=" * 70)
    
    sorted_findings = sorted(findings, key=lambda x: x['risk_score'], reverse=True)
    
    for i, f in enumerate(sorted_findings[:5], 1):
        print(f"\n[{i}] Resource: {f['resource_id']} ({f['resource_type']})")
        print(f"    Risk Score: {f['risk_score']} | Priority: {f['priority']}")
        print(f"    Cost: ${f['cost']} | Usage: {f['usage']}%")
        print(f"    Categories: {', '.join(f['categories'])}")
        print(f"    Issues ({len(f['issues'])}):")
        for issue in f['issues']:
            print(f"      - {issue}")
    
    print("\n" + "=" * 70)
    print("SUMMARY BY PRIORITY")
    print("=" * 70)
    
    critical = [f for f in findings if f['priority'] == 'CRITICAL']
    high = [f for f in findings if f['priority'] == 'HIGH']
    medium = [f for f in findings if f['priority'] == 'MEDIUM']
    low = [f for f in findings if f['priority'] == 'LOW']
    
    print(f"\n  CRITICAL: {len(critical)} resources (Score >= 100)")
    print(f"  HIGH:     {len(high)} resources (Score >= 60)")
    print(f"  MEDIUM:   {len(medium)} resources (Score >= 30)")
    print(f"  LOW:      {len(low)} resources (Score < 30)")
    
    print("\n" + "=" * 70)
    print("COST IMPACT ANALYSIS")
    print("=" * 70)
    
    total_cost = sum(f['cost'] for f in findings)
    critical_cost = sum(f['cost'] for f in critical)
    high_cost = sum(f['cost'] for f in high)
    
    print(f"\n  Total Cost at Risk: ${total_cost}")
    print(f"  CRITICAL Priority Cost: ${critical_cost}")
    print(f"  HIGH Priority Cost: ${high_cost}")
    print(f"  Potential Savings: ${critical_cost + high_cost}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
