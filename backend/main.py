import os
from parser.data_parser import DataParser
from engine.rule_engine import RuleEngine

def main():
    base_path = os.path.dirname(__file__)
    data_path = os.path.join(base_path, 'data', 'resources.json')
    rules_path = os.path.join(base_path, 'data', 'rules.json')
    output_path = os.path.join(base_path, 'data', 'findings.json')
    
    print("[1] Loading resources...")
    parser = DataParser(data_path)
    resources = parser.parse()
    print(f"    Loaded {len(resources)} resources")
    
    print("\n[2] Initializing Rule Engine...")
    engine = RuleEngine(rules_path)
    print(f"    Loaded {len(engine.rules)} rules")
    
    print("\n[3] Analyzing resources...")
    findings = engine.analyze(resources)
    print(f"    Found {len(findings)} issues")
    
    print("\n[4] Saving findings...")
    engine.save_findings(findings, output_path)
    print(f"    Saved to {output_path}")
    
    print("\n[5] Summary:")
    critical = sum(1 for f in findings if f['priority'] == 'CRITICAL')
    high = sum(1 for f in findings if f['priority'] == 'HIGH')
    medium = sum(1 for f in findings if f['priority'] == 'MEDIUM')
    low = sum(1 for f in findings if f['priority'] == 'LOW')
    
    print(f"    CRITICAL: {critical}")
    print(f"    HIGH: {high}")
    print(f"    MEDIUM: {medium}")
    print(f"    LOW: {low}")
    
    print("\n[6] Top 3 Critical Findings:")
    sorted_findings = sorted(findings, key=lambda x: x['risk_score'], reverse=True)
    for f in sorted_findings[:3]:
        print(f"\n    Resource: {f['resource_id']} ({f['resource_type']})")
        print(f"    Risk Score: {f['risk_score']} | Priority: {f['priority']}")
        print(f"    Issues: {', '.join(f['issues'])}")

if __name__ == "__main__":
    main()
