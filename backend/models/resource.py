class Resource:
    def __init__(
        self,
        # ── Base inventory ───────────────────────────────────────────────
        id, type, usage, public, encrypted, cost, logging, role,

        # ── AWS Config ───────────────────────────────────────────────────
        region="us-east-1",
        resource_name=None,
        tags=None,
        has_tags=True,
        created_days_ago=0,
        compliance_violations=None,
        compliance_violation_count=0,

        # ── AWS CloudTrail ───────────────────────────────────────────────
        last_activity_days=0,
        failed_logins=0,
        suspicious_api_calls=0,
        regions_accessed=None,

        # ── AWS Cost Explorer ────────────────────────────────────────────
        monthly_cost=None,
        cost_trend_pct=0.0,
        savings_potential=0.0,
        rightsizing="none",

        # ── AWS SecurityHub ──────────────────────────────────────────────
        vuln_count=0,
        open_ports=None,
        compliance_score=100,
        cve_count=0,
        ssh_exposed=False,
        rdp_exposed=False,

        # ── AWS CloudWatch Metrics ───────────────────────────────────────
        cpu_avg=0.0,
        memory_avg=0.0,
        network_in_gb=0.0,
        disk_utilization=0.0
    ):
        # Base
        self.id        = id
        self.type      = type
        self.usage     = usage
        self.public    = public
        self.encrypted = encrypted
        self.cost      = cost
        self.logging   = logging
        self.role      = role

        # AWS Config
        self.region                     = region
        self.resource_name              = resource_name or id
        self.tags                       = tags or {}
        self.has_tags                   = has_tags
        self.created_days_ago           = created_days_ago
        self.compliance_violations      = compliance_violations or []
        self.compliance_violation_count = compliance_violation_count

        # AWS CloudTrail
        self.last_activity_days   = last_activity_days
        self.failed_logins        = failed_logins
        self.suspicious_api_calls = suspicious_api_calls
        self.regions_accessed     = regions_accessed or ["us-east-1"]

        # AWS Cost Explorer
        self.monthly_cost      = monthly_cost if monthly_cost is not None else cost
        self.cost_trend_pct    = cost_trend_pct
        self.savings_potential = savings_potential
        self.rightsizing       = rightsizing

        # AWS SecurityHub
        self.vuln_count       = vuln_count
        self.open_ports       = open_ports or []
        self.compliance_score = compliance_score
        self.cve_count        = cve_count
        self.ssh_exposed      = ssh_exposed
        self.rdp_exposed      = rdp_exposed

        # AWS CloudWatch Metrics
        self.cpu_avg          = cpu_avg
        self.memory_avg       = memory_avg
        self.network_in_gb    = network_in_gb
        self.disk_utilization = disk_utilization

    def __repr__(self):
        return (
            f"Resource(id={self.id}, name={self.resource_name}, "
            f"type={self.type}, region={self.region})"
        )
