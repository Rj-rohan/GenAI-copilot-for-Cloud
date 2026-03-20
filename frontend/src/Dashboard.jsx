import { useState, useEffect, useCallback } from 'react';
import './Dashboard.css';

// ── Chart: Risk Distribution Donut ────────────────────────────────────────────
const DonutChart = ({ stats }) => {
  const total = (stats.critical||0) + (stats.high||0) + (stats.medium||0) + (stats.low||0);
  if (!total) return <div className="chart-empty">No data yet</div>;

  const slices = [
    { label: 'Critical', value: stats.critical||0, color: '#dc2626' },
    { label: 'High',     value: stats.high||0,     color: '#ea580c' },
    { label: 'Medium',   value: stats.medium||0,   color: '#eab308' },
    { label: 'Low',      value: stats.low||0,      color: '#22c55e' },
  ];

  const r = 58, cx = 80, cy = 80, circ = 2 * Math.PI * r;
  let cum = 0;

  return (
    <div className="donut-wrap">
      <svg viewBox="0 0 160 160" className="donut-svg">
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="#f3f4f6" strokeWidth="22" />
        {slices.map((s, i) => {
          const pct = s.value / total;
          const dash = `${pct * circ} ${circ}`;
          const rot  = cum * 360 - 90;
          cum += pct;
          return (
            <circle key={i} cx={cx} cy={cy} r={r}
              fill="none" stroke={s.color} strokeWidth="22"
              strokeDasharray={dash}
              transform={`rotate(${rot} ${cx} ${cy})`}
            />
          );
        })}
        <text x={cx} y={cy - 8}  textAnchor="middle" fontSize="24" fontWeight="700" fill="#1f2937">{total}</text>
        <text x={cx} y={cy + 12} textAnchor="middle" fontSize="11" fill="#6b7280">findings</text>
      </svg>
      <div className="donut-legend">
        {slices.map((s, i) => (
          <div key={i} className="legend-item">
            <span className="legend-dot" style={{ background: s.color }} />
            <span className="legend-label">{s.label}</span>
            <span className="legend-val">{s.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// ── Chart: Cost by Resource Type ──────────────────────────────────────────────
const CostBars = ({ findings }) => {
  if (!findings.length) return <div className="chart-empty">No data yet</div>;

  const TYPE_COLORS = { compute: '#3b82f6', storage: '#8b5cf6', database: '#06b6d4', network: '#10b981' };
  const costs = {}, savings = {};
  findings.forEach(f => {
    costs[f.resource_type]   = (costs[f.resource_type]   || 0) + (f.cost || 0);
    savings[f.resource_type] = (savings[f.resource_type] || 0) + (f.savings_potential || 0);
  });

  const rows   = Object.entries(costs).sort((a, b) => b[1] - a[1]);
  const maxVal = Math.max(...rows.map(([, v]) => v), 1);

  return (
    <div className="cost-bars">
      {rows.map(([type, cost]) => (
        <div key={type} className="bar-row">
          <span className="bar-label">{type}</span>
          <div className="bar-track">
            <div className="bar-fill"
              style={{ width: `${(cost / maxVal) * 100}%`, background: TYPE_COLORS[type] || '#6b7280' }}
            />
            <div className="bar-savings"
              style={{ width: `${((savings[type]||0) / maxVal) * 100}%` }}
            />
          </div>
          <div className="bar-nums">
            <span className="bar-cost">${cost}</span>
            <span className="bar-save">-${Math.round(savings[type]||0)}</span>
          </div>
        </div>
      ))}
      <div className="bar-legend-row">
        <span><span className="dot-blue" /> Monthly Cost</span>
        <span><span className="dot-yellow" /> Potential Savings</span>
      </div>
    </div>
  );
};

// ── Chart: Compliance Overview ────────────────────────────────────────────────
const CompliancePanel = ({ findings }) => {
  if (!findings.length) return <div className="chart-empty">No data yet</div>;

  const violations = {};
  findings.forEach(f =>
    (f.compliance_violations || []).forEach(v => { violations[v] = (violations[v] || 0) + 1; })
  );
  const sorted    = Object.entries(violations).sort((a, b) => b[1] - a[1]);
  const totalViol = sorted.reduce((s, [, c]) => s + c, 0);
  const avgScore  = Math.round(
    findings.reduce((s, f) => s + (f.compliance_score || 0), 0) / findings.length
  );
  const scoreColor = avgScore >= 80 ? '#22c55e' : avgScore >= 60 ? '#eab308' : '#dc2626';

  return (
    <div className="compliance-wrap">
      <div className="compliance-gauge">
        <svg viewBox="0 0 100 100" width="90" height="90">
          <circle cx="50" cy="50" r="40" fill="none" stroke="#e5e7eb" strokeWidth="10" />
          <circle cx="50" cy="50" r="40" fill="none" stroke={scoreColor} strokeWidth="10"
            strokeDasharray={`${(avgScore / 100) * 251} 251`}
            transform="rotate(-90 50 50)"
          />
          <text x="50" y="46" textAnchor="middle" fontSize="20" fontWeight="700" fill={scoreColor}>{avgScore}</text>
          <text x="50" y="62" textAnchor="middle" fontSize="9"  fill="#6b7280">Avg Score</text>
        </svg>
        <div className="total-viol">{totalViol} violations</div>
      </div>
      <div className="viol-list">
        {sorted.slice(0, 5).map(([v, count], i) => {
          const [std, ...rest] = v.split(':');
          return (
            <div key={i} className="viol-row">
              <span className="viol-std">{std.trim()}</span>
              <span className="viol-desc">{rest.join(':').trim()}</span>
              <span className="viol-count">{count}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ── Helpers ───────────────────────────────────────────────────────────────────
const getPriorityColor = p =>
  ({ CRITICAL: '#dc2626', HIGH: '#ea580c', MEDIUM: '#eab308', LOW: '#22c55e' }[p] || '#6b7280');

// ── Main Dashboard ────────────────────────────────────────────────────────────
const Dashboard = () => {
  const [findings,         setFindings]         = useState([]);
  const [stats,            setStats]            = useState({ total:0, critical:0, high:0, medium:0, low:0, totalCost:0, totalSavings:0 });
  const [selectedPriority, setSelectedPriority] = useState('ALL');
  const [selectedResource, setSelectedResource] = useState(null);
  const [copiedIssue,      setCopiedIssue]      = useState(null);
  const [generating,       setGenerating]       = useState(false);
  const [genMsg,           setGenMsg]           = useState('');

  useEffect(() => { loadFindings(); }, []);

  const loadFindings = async () => {
    try {
      const res  = await fetch(`/findings.json?t=${Date.now()}`);
      const data = await res.json();
      setFindings(data);
      setStats({
        total:        data.length,
        critical:     data.filter(f => f.priority === 'CRITICAL').length,
        high:         data.filter(f => f.priority === 'HIGH').length,
        medium:       data.filter(f => f.priority === 'MEDIUM').length,
        low:          data.filter(f => f.priority === 'LOW').length,
        totalCost:    data.reduce((s, f) => s + (f.cost || 0), 0),
        totalSavings: Math.round(data.reduce((s, f) => s + (f.savings_potential || 0), 0)),
      });
    } catch (e) { console.error('Error loading findings:', e); }
  };

  const generateData = async () => {
    setGenerating(true);
    setGenMsg('⏳ Generating fresh cloud data...');
    try {
      const res  = await fetch('http://localhost:5000/api/generate', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setGenMsg(`✅ Generated ${data.n_resources} resources successfully!`);
        setTimeout(async () => { await loadFindings(); setGenMsg(''); }, 1000);
      } else {
        setGenMsg('❌ Error: ' + (data.error || 'Unknown'));
      }
    } catch {
      setGenMsg('❌ Backend unreachable — make sure python api.py is running');
    } finally {
      setGenerating(false);
    }
  };

  const exportCSV = () => {
    const headers = ['Resource ID','Name','Type','Region','Priority','Risk Score','Cost/mo','Savings','Usage%','Compliance Score','Rightsizing','Issues'];
    const rows    = findings.map(f => [
      f.resource_id, f.resource_name, f.resource_type, f.region,
      f.priority, f.risk_score, f.cost, (f.savings_potential||0).toFixed(2),
      f.usage, f.compliance_score, f.rightsizing,
      `"${(f.issues||[]).join('; ')}"`
    ]);
    const csv  = [headers, ...rows].map(r => r.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url  = URL.createObjectURL(blob);
    const a    = Object.assign(document.createElement('a'), { href: url, download: `cloud-findings-${new Date().toISOString().slice(0,10)}.csv` });
    a.click();
    URL.revokeObjectURL(url);
  };

  const copyToClipboard = useCallback((issue, text) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedIssue(issue);
      setTimeout(() => setCopiedIssue(null), 2000);
    });
  }, []);

  const filtered = selectedPriority === 'ALL'
    ? findings
    : findings.filter(f => f.priority === selectedPriority);

  return (
    <div className="dashboard">

      {/* ── Header ── */}
      <header className="dashboard-header">
        <div className="header-text">
          <h1>🛡️ GenAI Cloud Security Copilot</h1>
          <p>Risk &amp; Cost Optimization — powered by Gemini AI</p>
        </div>
        <div className="header-actions">
          <button className="btn-generate" onClick={generateData} disabled={generating}>
            {generating ? '⏳ Generating...' : '🔄 Generate New Data'}
          </button>
          <button className="btn-export" onClick={exportCSV}>
            ⬇️ Export CSV
          </button>
        </div>
        {genMsg && <div className="gen-msg">{genMsg}</div>}
      </header>

      {/* ── Stats Grid ── */}
      <div className="stats-grid">
        <div className="stat-card total">    <div className="stat-value">{stats.total}</div>         <div className="stat-label">Total Issues</div></div>
        <div className="stat-card critical"> <div className="stat-value">{stats.critical}</div>      <div className="stat-label">Critical</div></div>
        <div className="stat-card high">     <div className="stat-value">{stats.high}</div>          <div className="stat-label">High</div></div>
        <div className="stat-card medium">   <div className="stat-value">{stats.medium}</div>        <div className="stat-label">Medium</div></div>
        <div className="stat-card low">      <div className="stat-value">{stats.low}</div>           <div className="stat-label">Low</div></div>
        <div className="stat-card cost">     <div className="stat-value">${stats.totalCost}</div>    <div className="stat-label">Cost at Risk/mo</div></div>
        <div className="stat-card savings">  <div className="stat-value">${stats.totalSavings}</div> <div className="stat-label">Potential Savings</div></div>
      </div>

      {/* ── Charts Row ── */}
      <div className="charts-row">
        <div className="chart-card">
          <div className="chart-title">📊 Risk Distribution</div>
          <DonutChart stats={stats} />
        </div>
        <div className="chart-card">
          <div className="chart-title">💰 Cost &amp; Savings by Resource Type</div>
          <CostBars findings={findings} />
        </div>
        <div className="chart-card">
          <div className="chart-title">🛡️ Compliance Overview</div>
          <CompliancePanel findings={findings} />
        </div>
      </div>

      {/* ── Filters ── */}
      <div className="filters">
        {['ALL','CRITICAL','HIGH','MEDIUM','LOW'].map(p => (
          <button key={p}
            className={selectedPriority === p ? 'active' : ''}
            onClick={() => setSelectedPriority(p)}
          >
            {p === 'ALL' ? 'All' : p.charAt(0) + p.slice(1).toLowerCase()}
          </button>
        ))}
        <span className="filter-count">{filtered.length} findings</span>
      </div>

      {/* ── Findings + Detail ── */}
      <div className="findings-container">

        {/* List */}
        <div className="findings-list">
          <h2>Findings ({filtered.length})</h2>
          {filtered.map(f => (
            <div key={f.resource_id}
              className={`finding-card ${selectedResource?.resource_id === f.resource_id ? 'selected' : ''}`}
              onClick={() => setSelectedResource(f)}
              style={{ borderLeftColor: getPriorityColor(f.priority) }}
            >
              <div className="finding-header">
                <span className="resource-id">{f.resource_id}</span>
                <span className="resource-name-small">{f.resource_name}</span>
                <span className="resource-type">{f.resource_type}</span>
                <span className="priority-badge" style={{ backgroundColor: getPriorityColor(f.priority) }}>{f.priority}</span>
              </div>
              <div className="finding-summary">{f.summary}</div>
              <div className="finding-meta">
                <span>🎯 {f.risk_score}</span>
                <span>💰 ${f.cost}/mo</span>
                <span>📊 {f.usage}% used</span>
                {f.vuln_count > 0 && <span className="vuln-chip">⚠️ {f.vuln_count} vulns</span>}
                {f.savings_potential > 0 && <span className="save-chip">💾 save ${Math.round(f.savings_potential)}</span>}
              </div>
            </div>
          ))}
        </div>

        {/* Detail Panel */}
        {selectedResource ? (
          <div className="finding-details">
            <div className="details-header">
              <h2>Resource Details</h2>
              <button onClick={() => setSelectedResource(null)}>✕</button>
            </div>

            {/* Identity */}
            <div className="detail-section">
              <h3>{selectedResource.resource_id} — {selectedResource.resource_name}</h3>
              <div className="identity-row">
                <span className="resource-type">{selectedResource.resource_type}</span>
                <span className="region-tag">📍 {selectedResource.region}</span>
                <span className="priority-badge large" style={{ backgroundColor: getPriorityColor(selectedResource.priority) }}>
                  {selectedResource.priority_tag} {selectedResource.priority}
                </span>
              </div>
            </div>

            {/* Key Metrics */}
            <div className="detail-section">
              <h4>Key Metrics</h4>
              <div className="metrics-grid">
                <div className="metric">
                  <span className="metric-label">Risk Score</span>
                  <span className="metric-value" style={{ color: getPriorityColor(selectedResource.priority) }}>{selectedResource.risk_score}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Usage</span>
                  <span className="metric-value">{selectedResource.usage}%</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Cost/mo</span>
                  <span className="metric-value">${selectedResource.cost}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Savings</span>
                  <span className="metric-value" style={{ color: '#16a34a' }}>${(selectedResource.savings_potential||0).toFixed(2)}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Compliance</span>
                  <span className="metric-value" style={{ color: selectedResource.compliance_score >= 80 ? '#22c55e' : selectedResource.compliance_score >= 60 ? '#eab308' : '#dc2626' }}>
                    {selectedResource.compliance_score}/100
                  </span>
                </div>
                <div className="metric">
                  <span className="metric-label">Rightsizing</span>
                  <span className={`metric-value rs-${selectedResource.rightsizing}`}>{selectedResource.rightsizing}</span>
                </div>
              </div>
            </div>

            {/* Performance */}
            <div className="detail-section">
              <h4>Performance (CloudWatch Metrics)</h4>
              <div className="perf-bars">
                {[
                  { label: 'CPU',    val: selectedResource.cpu_avg,          color: '#3b82f6' },
                  { label: 'Memory', val: selectedResource.memory_avg,       color: '#8b5cf6' },
                  { label: 'Disk',   val: selectedResource.disk_utilization, color: '#06b6d4' },
                ].map(m => (
                  <div key={m.label} className="perf-row">
                    <span className="perf-label">{m.label}</span>
                    <div className="perf-track">
                      <div className="perf-fill" style={{ width: `${Math.min(m.val||0, 100)}%`, background: m.color }} />
                    </div>
                    <span className="perf-val">{(m.val||0).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Security Signals */}
            <div className="detail-section">
              <h4>Security Signals (SecurityHub + CloudTrail)</h4>
              <div className="signals-grid">
                <div className={`signal ${selectedResource.vuln_count > 0 ? 'sig-bad' : 'sig-good'}`}>
                  <span className="sig-icon">{selectedResource.vuln_count > 0 ? '⚠️' : '✅'}</span>
                  <span className="sig-label">Vulnerabilities</span>
                  <span className="sig-val">{selectedResource.vuln_count} ({selectedResource.cve_count} CVEs)</span>
                </div>
                <div className={`signal ${selectedResource.failed_logins > 5 ? 'sig-bad' : 'sig-good'}`}>
                  <span className="sig-icon">{selectedResource.failed_logins > 5 ? '🔴' : '✅'}</span>
                  <span className="sig-label">Failed Logins</span>
                  <span className="sig-val">{selectedResource.failed_logins}</span>
                </div>
                <div className={`signal ${selectedResource.ssh_exposed ? 'sig-bad' : 'sig-good'}`}>
                  <span className="sig-icon">{selectedResource.ssh_exposed ? '🔓' : '🔒'}</span>
                  <span className="sig-label">SSH Exposed</span>
                  <span className="sig-val">{selectedResource.ssh_exposed ? 'YES — RISK' : 'No'}</span>
                </div>
                <div className={`signal ${selectedResource.rdp_exposed ? 'sig-bad' : 'sig-good'}`}>
                  <span className="sig-icon">{selectedResource.rdp_exposed ? '🔓' : '🔒'}</span>
                  <span className="sig-label">RDP Exposed</span>
                  <span className="sig-val">{selectedResource.rdp_exposed ? 'YES — RISK' : 'No'}</span>
                </div>
                <div className="signal sig-neutral">
                  <span className="sig-icon">🕐</span>
                  <span className="sig-label">Last Activity</span>
                  <span className="sig-val">{selectedResource.last_activity_days}d ago</span>
                </div>
                <div className={`signal ${selectedResource.suspicious_api_calls > 0 ? 'sig-bad' : 'sig-good'}`}>
                  <span className="sig-icon">{selectedResource.suspicious_api_calls > 0 ? '🚨' : '✅'}</span>
                  <span className="sig-label">Suspicious API</span>
                  <span className="sig-val">{selectedResource.suspicious_api_calls} calls</span>
                </div>
              </div>
            </div>

            {/* Issues */}
            <div className="detail-section">
              <h4>Issues Detected ({selectedResource.issues?.length})</h4>
              <ul className="issues-list">
                {(selectedResource.issues || []).map((issue, i) => (
                  <li key={i}>{issue}</li>
                ))}
              </ul>
            </div>

            {/* Compliance Violations */}
            {selectedResource.compliance_violations?.length > 0 && (
              <div className="detail-section">
                <h4>Compliance Violations ({selectedResource.compliance_violations.length})</h4>
                <div className="comp-violations">
                  {selectedResource.compliance_violations.map((v, i) => {
                    const [std, ...rest] = v.split(':');
                    return (
                      <div key={i} className="comp-violation">
                        <span className="comp-std">{std.trim()}</span>
                        <span className="comp-desc">{rest.join(':').trim()}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Impact */}
            <div className="detail-section">
              <h4>Risk Impact</h4>
              <p className="impact-text">{selectedResource.impact}</p>
            </div>

            {/* Recommendation */}
            <div className="detail-section">
              <h4>Recommended Fix</h4>
              <div className="recommendation-box">{selectedResource.recommendation}</div>
            </div>

            {/* Categories */}
            <div className="detail-section">
              <h4>Categories</h4>
              <div className="categories">
                {(selectedResource.categories || []).map((cat, i) => (
                  <span key={i} className="category-tag">{cat}</span>
                ))}
              </div>
            </div>

            {/* AWS CLI Fix Commands */}
            {selectedResource.cli_fixes && Object.keys(selectedResource.cli_fixes).length > 0 && (
              <div className="detail-section">
                <h4>🔧 AWS CLI Fix Commands</h4>
                <p className="cli-intro">
                  Run these to remediate. Replace <code>&lt;SG_ID&gt;</code>,{' '}
                  <code>&lt;ACCOUNT_ID&gt;</code> with your actual values.
                </p>
                {Object.entries(selectedResource.cli_fixes).map(([issue, cmds], i) => {
                  const cmdText = cmds.join('\n');
                  return (
                    <div key={i} className="cli-fix-block">
                      <div className="cli-issue-label">▸ {issue}</div>
                      <div className="cli-code-wrapper">
                        <button
                          className={`copy-btn ${copiedIssue === issue ? 'copied' : ''}`}
                          onClick={() => copyToClipboard(issue, cmdText)}
                        >
                          {copiedIssue === issue ? '✓ Copied' : 'Copy'}
                        </button>
                        <pre className="cli-code">{cmdText}</pre>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ) : (
          <div className="detail-placeholder">
            <div className="ph-icon">🔍</div>
            <div className="ph-title">Select a resource</div>
            <div className="ph-text">
              Click any finding on the left to view full details — security signals, compliance violations, performance metrics, and AWS CLI fix commands.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
