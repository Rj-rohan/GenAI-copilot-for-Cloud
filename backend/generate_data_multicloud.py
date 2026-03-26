"""
generate_data.py - Cloud-Agnostic Version
==========================================
Generates simulated cloud data for AWS, Azure, and GCP.

Usage:
    python generate_data.py                    # AWS (default), 50 resources
    python generate_data.py --provider azure   # Azure, 50 resources
    python generate_data.py --provider gcp     # GCP, 50 resources
    python generate_data.py --provider all     # All 3 clouds, 50 each
    python generate_data.py --count 100        # AWS, 100 resources
    python generate_data.py --provider azure --count 75
"""

import random
import json
import os
import sys
import subprocess
import argparse
import time
from datetime import datetime

# Don't set seed at module level - we'll do it per generation
# random.seed(None)

BASE_PATH    = os.path.dirname(os.path.abspath(__file__))
DATA_PATH    = os.path.join(BASE_PATH, 'data')
SOURCES_PATH = os.path.join(DATA_PATH, 'sources')

# ── Cloud Provider Configurations ────────────────────────────────────────────

CLOUD_CONFIGS = {
    'aws': {
        'name': 'Amazon Web Services',
        'prefix': {'compute': 'ec2', 'storage': 's3', 'database': 'rds', 'network': 'alb'},
        'regions': ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-south-1', 'eu-central-1'],
        'region_weights': [0.40, 0.20, 0.20, 0.15, 0.05],
        'services': {
            'activity': 'CloudTrail',
            'config': 'AWS Config',
            'cost': 'Cost Explorer',
            'security': 'Security Hub',
            'metrics': 'CloudWatch'
        }
    },
    'azure': {
        'name': 'Microsoft Azure',
        'prefix': {'compute': 'vm', 'storage': 'blob', 'database': 'sqldb', 'network': 'lb'},
        'regions': ['eastus', 'westus2', 'westeurope', 'southeastasia', 'centralindia'],
        'region_weights': [0.35, 0.25, 0.20, 0.15, 0.05],
        'services': {
            'activity': 'Activity Log',
            'config': 'Resource Graph',
            'cost': 'Cost Management',
            'security': 'Security Center',
            'metrics': 'Azure Monitor'
        }
    },
    'gcp': {
        'name': 'Google Cloud Platform',
        'prefix': {'compute': 'gce', 'storage': 'gcs', 'database': 'cloudsql', 'network': 'gclb'},
        'regions': ['us-east1', 'us-west1', 'europe-west1', 'asia-south1', 'asia-southeast1'],
        'region_weights': [0.35, 0.25, 0.20, 0.15, 0.05],
        'services': {
            'activity': 'Cloud Audit Logs',
            'config': 'Asset Inventory',
            'cost': 'Cloud Billing',
            'security': 'Security Command Center',
            'metrics': 'Cloud Monitoring'
        }
    }
}

# ── Resource type distribution ───────────────────────────────────────────────
TYPE_DIST = [('compute', 0.40), ('storage', 0.25), ('database', 0.20), ('network', 0.15)]

NAME_POOL = {
    'compute':  ['web-server', 'api-server', 'app-server', 'batch-worker', 'ml-instance',
                 'bastion', 'admin-host', 'cache-node', 'proxy-server', 'microservice'],
    'storage':  ['user-uploads', 'static-assets', 'backup-store', 'log-archive',
                 'build-artifacts', 'raw-data-lake', 'processed-data', 'public-assets'],
    'database': ['primary-db', 'replica-db', 'analytics-db', 'staging-db', 'dev-db',
                 'reporting-db', 'auth-db', 'warehouse-db', 'metrics-db'],
    'network':  ['internet-lb', 'public-lb', 'internal-lb', 'api-gateway', 'legacy-lb'],
}

PUBLIC_PROB    = {'storage': 0.35, 'network': 0.45, 'compute': 0.10, 'database': 0.05}
ENCRYPTED_PROB = {'compute': 0.72, 'storage': 0.65, 'database': 0.88, 'network': 0.50}
LOGGING_PROB   = 0.65
ROLES          = ['user'] * 3 + ['admin']
COST_RANGES    = {'compute': (3, 18), 'storage': (1, 5), 'database': (10, 30), 'network': (2, 8)}

TEAMS    = ['backend', 'data', 'ml', 'platform', 'infra', 'security', 'devops']
PROJECTS = ['core-api', 'data-platform', 'ml-pipeline', 'infra-base', 'payments', 'auth-service']

PORTS = {
    'compute':  {'public': [22, 80, 443], 'private': [80, 443, 8080]},
    'storage':  {'public': [80, 443],     'private': [443]},
    'database': {'public': [3306, 1433],  'private': [3306]},
    'network':  {'public': [22, 80, 443, 3389], 'private': [80, 443]},
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def wt_choice(items, weights):
    r, cumulative = random.random(), 0
    for item, w in zip(items, weights):
        cumulative += w
        if r < cumulative:
            return item
    return items[-1]

def gen_usage():
    r = random.random()
    if   r < 0.15: return 0
    elif r < 0.40: return random.randint(1, 4)
    elif r < 0.60: return random.randint(5, 20)
    elif r < 0.80: return random.randint(20, 60)
    else:          return random.randint(60, 100)

# ── Generator functions ───────────────────────────────────────────────────────

def gen_inventory(n, provider='aws'):
    config = CLOUD_CONFIGS[provider]
    types = []
    for rtype, prob in TYPE_DIST:
        types.extend([rtype] * max(1, int(n * prob)))
    while len(types) < n:
        types.append('compute')
    types = types[:n]
    random.shuffle(types)

    used_names = {}
    resources  = []

    for i, rtype in enumerate(types):
        base = random.choice(NAME_POOL[rtype])
        used_names.setdefault(rtype, {})
        used_names[rtype][base] = used_names[rtype].get(base, 0) + 1
        count  = used_names[rtype][base]
        suffix = f"-{count:02d}" if count > 1 else ""

        usage      = gen_usage()
        is_public  = random.random() < PUBLIC_PROB[rtype]
        enc_prob   = ENCRYPTED_PROB[rtype] * (0.6 if is_public else 1.0)
        is_enc     = random.random() < enc_prob
        log_prob   = LOGGING_PROB * (0.65 if is_public else 1.0)
        is_log     = random.random() < log_prob
        cost       = random.randint(*COST_RANGES[rtype])
        role       = random.choice(ROLES)

        resources.append({
            'id':        f"r{i + 1}",
            'type':      rtype,
            'usage':     usage,
            'public':    is_public,
            'encrypted': is_enc,
            'cost':      cost,
            'logging':   is_log,
            'role':      role,
            'provider':  provider,
            '_name_base': base,
            '_suffix':    suffix,
        })

    return resources

def gen_cloudtrail(resources, provider='aws'):
    data = {}
    for r in resources:
        is_pub = r['public']
        role   = r['role']
        usage  = r['usage']

        if is_pub:
            failed      = random.randint(5, 22)
            suspicious  = random.randint(1, 6)
        elif role == 'admin':
            failed      = random.randint(2, 7)
            suspicious  = random.randint(0, 3)
        else:
            failed      = random.randint(0, 2)
            suspicious  = 0

        if   usage == 0: last = random.randint(90, 200)
        elif usage < 5:  last = random.randint(20, 90)
        elif usage < 20: last = random.randint(2, 20)
        else:            last = random.randint(1, 5)

        config = CLOUD_CONFIGS[provider]
        n_regions = random.randint(1, 3) if (is_pub or role == 'admin') else 1
        regions   = random.sample(config['regions'], min(n_regions, len(config['regions'])))

        data[r['id']] = {
            'last_activity_days':   last,
            'failed_logins':        failed,
            'suspicious_api_calls': suspicious,
            'regions_accessed':     regions,
        }
    return data

def gen_config(resources, provider='aws'):
    config = CLOUD_CONFIGS[provider]
    data = {}
    
    for r in resources:
        rtype    = r['type']
        is_pub   = r['public']
        is_enc   = r['encrypted']
        is_log   = r['logging']
        usage    = r['usage']

        prefix = config['prefix'][rtype]
        name   = f"{prefix}-{r['_name_base']}{r['_suffix']}"
        region = wt_choice(config['regions'], config['region_weights'])

        if usage > 20 and not is_pub:
            tags = {
                'env':     random.choice(['prod', 'staging']),
                'team':    random.choice(TEAMS),
                'project': random.choice(PROJECTS),
                'cloud':   provider
            }
        elif usage > 5:
            tags = {'env': random.choice(['dev', 'staging', 'prod']), 'cloud': provider}
        elif random.random() < 0.25:
            tags = {'env': 'dev', 'cloud': provider}
        else:
            tags = {'cloud': provider}

        violations = []
        if not is_enc:   violations.append('Data encryption required')
        if is_pub:       violations.append('Restrict public access')
        if not is_log:   violations.append('Audit logging required')
        if usage == 0:   violations.append('Unused resource consuming budget')

        data[r['id']] = {
            'region':               region,
            'resource_name':        name,
            'tags':                 tags,
            'created_days_ago':     random.randint(30, 550),
            'compliance_violations': violations,
        }
    return data

def gen_cost(resources):
    data = {}
    for r in resources:
        cost  = r['cost']
        usage = r['usage']

        if usage == 0:
            trend      = round(random.uniform(10, 20), 1)
            savings    = round(cost * 1.0, 2)
            rightsizing = 'terminate'
        elif usage < 5:
            trend      = round(random.uniform(5, 12), 1)
            savings    = round(cost * random.uniform(0.60, 0.85), 2)
            rightsizing = random.choice(['downsize', 'terminate'])
        elif usage < 20:
            trend      = round(random.uniform(2, 8), 1)
            savings    = round(cost * random.uniform(0.20, 0.50), 2)
            rightsizing = 'downsize'
        else:
            trend      = round(random.uniform(-5, 3), 1)
            savings    = round(cost * random.uniform(0, 0.12), 2)
            rightsizing = 'none'

        data[r['id']] = {
            'monthly_cost':      cost,
            'cost_trend_pct':    trend,
            'savings_potential': savings,
            'rightsizing':       rightsizing,
        }
    return data

def gen_securityhub(resources):
    data = {}
    for r in resources:
        rtype  = r['type']
        is_pub = r['public']
        is_enc = r['encrypted']

        if not is_enc and is_pub:
            vuln, cve = random.randint(4, 9), random.randint(2, 5)
        elif not is_enc:
            vuln, cve = random.randint(2, 5), random.randint(0, 2)
        elif is_pub:
            vuln, cve = random.randint(1, 4), random.randint(0, 2)
        else:
            vuln, cve = random.randint(0, 1), 0

        open_ports = list(PORTS[rtype]['public' if is_pub else 'private'])

        score = 100
        if not is_enc:        score -= 20
        if not r['logging']:  score -= 15
        if is_pub:            score -= 15
        if vuln > 3:          score -= 10
        score = max(15, score + random.randint(-5, 5))

        data[r['id']] = {
            'vuln_count':       vuln,
            'open_ports':       open_ports,
            'compliance_score': score,
            'cve_count':        cve,
        }
    return data

def gen_metrics(resources):
    data = {}
    for r in resources:
        usage = r['usage']
        cpu    = round(max(0.0, min(100.0, usage + random.uniform(-2, 2))), 1)
        memory = round(min(100.0, usage * 1.5 + random.uniform(5, 15)), 1)
        net    = round(usage * random.uniform(0.3, 1.5), 2)
        disk   = round(random.uniform(5, min(95, usage + 30)), 1)

        data[r['id']] = {
            'cpu_avg':          cpu,
            'memory_avg':       memory,
            'network_in_gb':    net,
            'disk_utilization': disk,
        }
    return data

# ── I/O helpers ───────────────────────────────────────────────────────────────

def save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)

def clean(resources):
    return [{k: v for k, v in r.items() if not k.startswith('_')} for r in resources]

# ── Main ──────────────────────────────────────────────────────────────────────

def generate_for_provider(provider, n):
    # Reseed with current time + process ID for true randomness
    random.seed(int(time.time() * 1000) + os.getpid())
    
    config = CLOUD_CONFIGS[provider]
    print(f"\n{'='*60}")
    print(f"  {config['name']} ({provider.upper()})")
    print(f"  Generating {n} resources...")
    print(f"{'='*60}")

    resources = gen_inventory(n, provider)
    ct_data   = gen_cloudtrail(resources, provider)
    cfg_data  = gen_config(resources, provider)
    cost_data = gen_cost(resources)
    sh_data   = gen_securityhub(resources)
    met_data  = gen_metrics(resources)

    # Save with provider prefix
    save(os.path.join(DATA_PATH, f'resources_{provider}.json'), clean(resources))
    save(os.path.join(SOURCES_PATH, f'cloudtrail_{provider}.json'), ct_data)
    save(os.path.join(SOURCES_PATH, f'config_{provider}.json'), cfg_data)
    save(os.path.join(SOURCES_PATH, f'cost_{provider}.json'), cost_data)
    save(os.path.join(SOURCES_PATH, f'securityhub_{provider}.json'), sh_data)
    save(os.path.join(SOURCES_PATH, f'metrics_{provider}.json'), met_data)

    # Also save as default (for backward compatibility)
    if provider == 'aws':
        save(os.path.join(DATA_PATH, 'resources.json'), clean(resources))
        save(os.path.join(SOURCES_PATH, 'cloudtrail.json'), ct_data)
        save(os.path.join(SOURCES_PATH, 'config.json'), cfg_data)
        save(os.path.join(SOURCES_PATH, 'cost.json'), cost_data)
        save(os.path.join(SOURCES_PATH, 'securityhub.json'), sh_data)
        save(os.path.join(SOURCES_PATH, 'metrics.json'), met_data)

    # Print stats
    type_counts = {}
    for r in resources:
        type_counts[r['type']] = type_counts.get(r['type'], 0) + 1

    print(f"\n[1] Inventory ({n} resources)")
    for rtype, cnt in sorted(type_counts.items()):
        pub = sum(1 for r in resources if r['type'] == rtype and r['public'])
        print(f"    {rtype:<10}: {cnt:>3} resources  ({pub} public)")

    pub_total = sum(1 for r in resources if r['public'])
    no_enc    = sum(1 for r in resources if not r['encrypted'])
    no_log    = sum(1 for r in resources if not r['logging'])
    idle      = sum(1 for r in resources if r['usage'] < 5)
    unused    = sum(1 for r in resources if r['usage'] == 0)

    print(f"\n[2] Security Posture")
    print(f"    Public resources  : {pub_total}")
    print(f"    Unencrypted       : {no_enc}")
    print(f"    No logging        : {no_log}")
    print(f"    Idle (usage < 5%) : {idle}")
    print(f"    Unused (usage = 0): {unused}")

    print(f"\n[3] Source Files Written")
    print(f"    data/resources_{provider}.json")
    print(f"    data/sources/cloudtrail_{provider}.json")
    print(f"    data/sources/config_{provider}.json")
    print(f"    data/sources/cost_{provider}.json")
    print(f"    data/sources/securityhub_{provider}.json")
    print(f"    data/sources/metrics_{provider}.json")

def main():
    parser = argparse.ArgumentParser(description='Generate cloud-agnostic simulated data')
    parser.add_argument('--provider', '-p', choices=['aws', 'azure', 'gcp', 'all'], 
                        default='aws', help='Cloud provider (default: aws)')
    parser.add_argument('--count', '-c', type=int, default=50, 
                        help='Number of resources to generate (default: 50)')
    
    args = parser.parse_args()

    ts = datetime.now().strftime('%H:%M:%S')
    print("=" * 60)
    print(f"  GenAI Cloud Security Copilot - Multi-Cloud")
    print(f"  Run at: {ts}")
    print("=" * 60)

    if args.provider == 'all':
        for provider in ['aws', 'azure', 'gcp']:
            generate_for_provider(provider, args.count)
    else:
        generate_for_provider(args.provider, args.count)

    # Run analysis for the primary provider
    primary_provider = 'aws' if args.provider == 'all' else args.provider
    print(f"\n[4] Running Analysis Pipeline for {primary_provider.upper()}...")
    result = subprocess.run(
        [sys.executable, os.path.join(BASE_PATH, 'main.py'), '--provider', primary_provider],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            if any(x in line for x in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'TOTAL',
                                         'Cost at Risk', 'Savings', 'Vuln', 'Login']):
                print(f"    {line.strip()}")
        print(f"\n    Findings saved to data/findings_{primary_provider}.json")
    else:
        print("    Pipeline error:")
        print(result.stderr[-500:])

    print(f"\n[DONE] Dataset ready for {args.provider.upper()}. Start server: python api.py")

if __name__ == '__main__':
    main()
