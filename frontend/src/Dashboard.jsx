import { useState, useEffect, useCallback } from 'react';
import './Dashboard.css';

// ── Helpers ───────────────────────────────────────────────────────────────────
const PC = { CRITICAL: '#dc2626', HIGH: '#ea580c', MEDIUM: '#d97706', LOW: '#16a34a' };
const pc = p => PC[p] || '#64748b';

const CAT_COLOR = { security: '#dc2626', compliance: '#7c3aed', cost: '#ea580c', access: '#2563eb' };

// ── Donut Chart ───────────────────────────────────────────────────────────────
const DonutChart = ({ stats }) => {
  const data = [
    { label: 'Critical', v: stats.critical || 0, c: '#dc2626' },
    { label: 'High',     v: stats.high     || 0, c: '#ea580c' },
    { label: 'Medium',   v: stats.medium   || 0, c: '#d97706' },
    { label: 'Low',      v: stats.low      || 0, c: '#16a34a' },
  ];
  const total = data.reduce((s, d) => s + d.v, 0);
  if (!total) return <div className="chart-empty">No data</div>;

  const r = 52, cx = 70, cy = 70, circ = 2 * Math.PI * r;
  let cum = 0;

  return (
    <div className="donut-wrap">
      <svg viewBox="0 0 140 140" width="130" height="130">
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="#f1f5f9" strokeWidth="20" />
        {data.map((d, i) => {
          const pct = d.v / total;
          const rot = cum * 360 - 90;
          cum += pct;
          return (
            <circle key={i} cx={cx} cy={cy} r={r}
              fill="none" stroke={d.c} strokeWidth="20"
              strokeDasharray={`${pct * circ} ${circ}`}
              transform={`rotate(${rot} ${cx} ${cy})`}
            />
          );
        })}
        <text x={cx} y={cy - 7}  textAnchor="middle" fontSize="24" fontWeight="800" fill="#0f172a">{total}</text>
        <text x={cx} y={cy + 12} textAnchor="middle" fontSize="10" fill="#94a3b8">findings</text>
      </svg>
      <div className="donut-legend">
        {data.map((d, i) => (
          <div key={i} className="dl-row">
            <span className="dl-dot" style={{ background: d.c }} />
            <span className="dl-label">{d.label}</span>
            <span className="dl-val">{d.v}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// ── Cost Bar Chart ────────────────────────────────────────────────────────────
const CostChart = ({ findings }) => {
  if (!findings.length) return <div className="chart-empty">No data</div>;
  const TC = { compute: '#3b82f6', storage: '#8b5cf6', database: '#06b6d4', network: '#10b981' };
  const costs = {}, saves = {};
  findings.forEach(f => {
    costs[f.resource_type] = (costs[f.resource_type] || 0) + (f.cost || 0);
    saves[f.resource_type] = (saves[f.resource_type] || 0) + (f.savings_potential || 0);
  });
  const rows = Object.entries(costs).sort((a, b) => b[1] - a[1]);
  const max  = Math.max(...rows.map(([, v]) => v), 1);

  return (
    <div className="cost-wrap">
      {rows.map(([t, c]) => (
        <div key={t} className="cb-row">
          <span className="cb-type">{t}</span>
          <div className="cb-track">
            <div className="cb-fill" style={{ width: `${(c / max) * 100}%`, background: TC[t] || '#6b7280' }} />
          </div>
          <div className="cb-nums">
            <span className="cb-cost">${c}</span>
            <span className="cb-save">↓${Math.round(saves[t] || 0)}</span>
          </div>
        </div>
      ))}
      <div className="cb-legend">
        <span><i className="leg-dot" style={{ background: '#3b82f6' }} />Cost</span>
        <span><i className="leg-dot" style={{ background: '#059669' }} />Savings</span>
      </div>
    </div>
  );
};

// ── Compliance Chart ──────────────────────────────────────────────────────────
const ComplianceChart = ({ findings }) => {
  if (!findings.length) return <div className="chart-empty">No data</div>;
  const viols = {};
  findings.forEach(f => (f.compliance_violations || []).forEach(v => { viols[v] = (viols[v] || 0) + 1; }));
  const total  = Object.values(viols).reduce((s, v) => s + v, 0);
  const avg    = Math.round(findings.reduce((s, f) => s + (f.compliance_score || 0), 0) / findings.length);
  const sc     = avg >= 80 ? '#16a34a' : avg >= 60 ? '#d97706' : '#dc2626';
  const sorted = Object.entries(viols).sort((a, b) => b[1] - a[1]);

  return (
    <div className="comp-wrap">
      <div className="comp-gauge-row">
        <svg viewBox="0 0 100 100" width="80" height="80">
          <circle cx="50" cy="50" r="38" fill="none" stroke="#f1f5f9" strokeWidth="10" />
          <circle cx="50" cy="50" r="38" fill="none" stroke={sc} strokeWidth="10"
            strokeDasharray={`${(avg / 100) * 239} 239`} transform="rotate(-90 50 50)" />
          <text x="50" y="46" textAnchor="middle" fontSize="20" fontWeight="800" fill={sc}>{avg}</text>
          <text x="50" y="61" textAnchor="middle" fontSize="9"  fill="#94a3b8">score</text>
        </svg>
        <div className="comp-gauge-info">
          <div className="comp-gauge-label">Avg Compliance Score</div>
          <div className="comp-gauge-total">{total} total violations</div>
        </div>
      </div>
      <div className="comp-viol-list">
        {sorted.slice(0, 4).map(([v, c], i) => {
          const [std, ...rest] = v.split(':');
          return (
            <div key={i} className="cv-row">
              <span className="cv-std">{std.trim()}</span>
              <span className="cv-desc">{rest.join(':').trim()}</span>
              <span className="cv-cnt">{c}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ── Priority Action Queue ─────────────────────────────────────────────────────
const PriorityQueue = ({ findings, onOpen }) => {
  const top = findings
    .filter(f => f.priority === 'CRITICAL' || f.priority === 'HIGH')
    .slice(0, 5);

  if (!top.length) return null;

  return (
    <div className="pq-panel panel">
      <div className="panel-hdr">
        <span className="panel-title">⚑ Priority Action Queue</span>
        <span className="pq-sub">Ranked by risk score — fix in this order</span>
      </div>
      <div className="pq-list">
        {top.map((f, i) => (
          <div key={f.resource_id} className="pq-row" onClick={() => onOpen(f)}>
            <div className="pq-rank" style={{ background: pc(f.priority) + '18', color: pc(f.priority) }}>
              #{i + 1}
            </div>
            <div className="pq-info">
              <div className="pq-name">
                <span className="pq-id">{f.resource_id}</span>
                <span className="pq-rname">{f.resource_name}</span>
              </div>
              <div className="pq-issues">
                {(f.issues || []).slice(0, 2).map((iss, j) => (
                  <span key={j} className="pq-issue-tag">{iss}</span>
                ))}
              </div>
            </div>
            <div className="pq-right">
              <div className="pq-score" style={{ color: pc(f.priority) }}>{f.risk_score}</div>
              <span className="chip-pri" style={{ color: pc(f.priority), background: pc(f.priority) + '18', borderColor: pc(f.priority) + '44' }}>
                {f.priority}
              </span>
              <span className="pq-arrow">→</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ── Score Breakdown ───────────────────────────────────────────────────────────
const ScoreBreakdown = ({ finding }) => {
  const bd = finding.score_breakdown;
  if (!bd || !bd.rules_triggered) return null;

  const catColor = c => CAT_COLOR[c] || '#64748b';
  const thresholds = { CRITICAL: 100, HIGH: 60, MEDIUM: 30, LOW: 0 };
  const thresh = thresholds[finding.priority] || 0;

  return (
    <div className="ds">
      <div className="ds-title">Risk Score Breakdown</div>

      {/* Formula bar */}
      <div className="score-formula">
        <div className="sf-eq">
          <span className="sf-box sf-base">{bd.base_score}<small>rules</small></span>
          <span className="sf-op">+</span>
          <span className="sf-box sf-cost">{bd.cost_factor}<small>cost</small></span>
          <span className="sf-op">+</span>
          <span className="sf-box sf-usage">{bd.usage_penalty}<small>idle</small></span>
          <span className="sf-op">×</span>
          <span className="sf-box sf-exp">{bd.exposure_multiplier}×<small>exposure</small></span>
          <span className="sf-op">=</span>
          <span className="sf-box sf-total" style={{ background: pc(finding.priority) + '18', color: pc(finding.priority), borderColor: pc(finding.priority) + '55' }}>
            {bd.final_score}<small>score</small>
          </span>
        </div>
        <div className="sf-thresh">
          Threshold: <strong>{finding.priority}</strong> ≥ {thresh} pts
        </div>
      </div>

      {/* Rules that fired */}
      <div className="sb-rules-title">Rules Triggered ({bd.rules_triggered.length})</div>
      {bd.rules_triggered.map((r, i) => (
        <div key={i} className="sb-rule-row">
          <span className="sb-rule-id">{r.id}</span>
          <span className="sb-rule-cat" style={{ background: catColor(r.category) + '18', color: catColor(r.category) }}>
            {r.category}
          </span>
          <span className="sb-rule-msg">{r.message}</span>
          <span className="sb-rule-calc">{r.risk} × {r.weight} = <strong>{r.weighted}</strong></span>
        </div>
      ))}
    </div>
  );
};

// ── Dashboard ─────────────────────────────────────────────────────────────────
export default function Dashboard({ cloud = 'aws' }) {
  const [findings,   setFindings]   = useState([]);
  const [stats,      setStats]      = useState({ total: 0, critical: 0, high: 0, medium: 0, low: 0, totalCost: 0, totalSavings: 0 });
  const [filter,     setFilter]     = useState('ALL');
  const [selected,   setSelected]   = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [copied,     setCopied]     = useState(null);
  const [generating, setGenerating] = useState(false);
  const [genMsg,     setGenMsg]     = useState('');
  const [sortBy,     setSortBy]     = useState('risk_score');
  const [sortDir,    setSortDir]    = useState('desc');

  useEffect(() => { load(); }, [cloud]);

  const load = async () => {
    try {
      const res  = await fetch(`/findings_${cloud}.json?t=${Date.now()}`);
      const data = await res.json();
      // Sort by risk_score descending by default (highest risk first)
      const sorted = [...data].sort((a, b) => b.risk_score - a.risk_score);
      setFindings(sorted);
      setStats({
        total:        data.length,
        critical:     data.filter(f => f.priority === 'CRITICAL').length,
        high:         data.filter(f => f.priority === 'HIGH').length,
        medium:       data.filter(f => f.priority === 'MEDIUM').length,
        low:          data.filter(f => f.priority === 'LOW').length,
        totalCost:    data.reduce((s, f) => s + (f.cost || 0), 0),
        totalSavings: Math.round(data.reduce((s, f) => s + (f.savings_potential || 0), 0)),
      });
    } catch (e) { 
      console.error(e);
      setFindings([]);
      setStats({ total: 0, critical: 0, high: 0, medium: 0, low: 0, totalCost: 0, totalSavings: 0 });
    }
  };

  const generate = async () => {
    setGenerating(true); setGenMsg('Generating…');
    try {
      const res = await fetch('http://localhost:5000/api/generate', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: cloud })
      });
      const d   = await res.json();
      if (d.success) { 
        setGenMsg(`✓ ${d.n_resources} resources generated for ${cloud.toUpperCase()}`); 
        setTimeout(async () => { await load(); setGenMsg(''); }, 900); 
      }
      else setGenMsg('Error: ' + d.error);
    } catch { setGenMsg('Backend offline'); }
    finally { setGenerating(false); }
  };

  const exportCSV = () => {
    const h = ['ID','Name','Type','Region','Priority','Risk','Cost','Savings','Usage%','Compliance','Rightsizing','Issues'];
    const r = findings.map(f => [f.resource_id, f.resource_name, f.resource_type, f.region, f.priority, f.risk_score, f.cost, (f.savings_potential||0).toFixed(2), f.usage, f.compliance_score, f.rightsizing, `"${(f.issues||[]).join('; ')}"`]);
    const a = Object.assign(document.createElement('a'), {
      href: URL.createObjectURL(new Blob([[h, ...r].map(row => row.join(',')).join('\n')], { type: 'text/csv' })),
      download: `findings-${new Date().toISOString().slice(0,10)}.csv`
    });
    a.click();
  };

  const copy = useCallback((key, text) => {
    navigator.clipboard.writeText(text).then(() => { setCopied(key); setTimeout(() => setCopied(null), 2000); });
  }, []);

  const openDrawer  = f  => { setSelected(f); setDrawerOpen(true); };
  const closeDrawer = () => { setDrawerOpen(false); setTimeout(() => setSelected(null), 240); };

  // Sort + filter
  const toggleSort = (col) => {
    if (sortBy === col) setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    else { setSortBy(col); setSortDir('desc'); }
  };

  const baseFiltered = filter === 'ALL' ? findings : findings.filter(f => f.priority === filter);
  const filtered = [...baseFiltered].sort((a, b) => {
    const av = a[sortBy] ?? 0, bv = b[sortBy] ?? 0;
    if (typeof av === 'string') return sortDir === 'asc' ? av.localeCompare(bv) : bv.localeCompare(av);
    return sortDir === 'asc' ? av - bv : bv - av;
  });

  const SortIcon = ({ col }) => {
    if (sortBy !== col) return <span className="sort-icon sort-none">⇅</span>;
    return <span className="sort-icon sort-active">{sortDir === 'asc' ? '↑' : '↓'}</span>;
  };

  const TABS = [
    { k: 'ALL',      label: 'All',      n: stats.total    },
    { k: 'CRITICAL', label: 'Critical', n: stats.critical },
    { k: 'HIGH',     label: 'High',     n: stats.high     },
    { k: 'MEDIUM',   label: 'Medium',   n: stats.medium   },
    { k: 'LOW',      label: 'Low',      n: stats.low      },
  ];

  return (
    <div className="db">

      {/* ── Page Header ── */}
      <div className="page-hdr">
        <div className="page-hdr-left">
          <h1 className="page-title">{cloud.toUpperCase()} Security Overview</h1>
          <p className="page-sub">
            {stats.total} resources monitored · sorted by risk score
            {genMsg && <span className={`gen-msg ${genMsg.startsWith('✓') ? 'ok' : ''}`}> · {genMsg}</span>}
          </p>
        </div>
        <div className="page-hdr-right">
          <button className="btn-sec" onClick={load}>🔄 Refresh</button>
          <button className="btn-sec" onClick={exportCSV}>↓ Export CSV</button>
          <button className="btn-pri" onClick={generate} disabled={generating}>
            {generating ? '⟳ Generating…' : '⟳ Generate Data'}
          </button>
        </div>
      </div>

      {/* ── Alert Bar ── */}
      {stats.critical > 0 && (
        <div className="alert-bar">
          <span className="alert-icon">⚠</span>
          <span><strong>{stats.critical} CRITICAL</strong> findings require immediate attention — potential data breach &amp; compliance violation risk</span>
          <button className="alert-cta" onClick={() => setFilter('CRITICAL')}>View Critical →</button>
        </div>
      )}

      {/* ── Stat Tiles ── */}
      <div className="stat-row">
        {[
          { label: 'Total Findings',    val: stats.total,           color: '#2563eb', bg: '#eff6ff' },
          { label: 'Critical',          val: stats.critical,        color: '#dc2626', bg: '#fef2f2' },
          { label: 'High',              val: stats.high,            color: '#ea580c', bg: '#fff7ed' },
          { label: 'Medium',            val: stats.medium,          color: '#d97706', bg: '#fffbeb' },
          { label: 'Low',               val: stats.low,             color: '#16a34a', bg: '#f0fdf4' },
          { label: 'Cost at Risk / mo', val: `$${stats.totalCost}`,  color: '#7c3aed', bg: '#f5f3ff' },
          { label: 'Potential Savings', val: `$${stats.totalSavings}`,color: '#059669', bg: '#ecfdf5' },
        ].map((s, i) => (
          <div key={i} className="stat-tile" style={{ '--tile-color': s.color, '--tile-bg': s.bg }}>
            <div className="st-label">{s.label}</div>
            <div className="st-val">{s.val}</div>
          </div>
        ))}
      </div>

      {/* ── Priority Action Queue ── */}
      <PriorityQueue findings={findings} onOpen={openDrawer} />

      {/* ── Charts Row ── */}
      <div className="charts-row">
        <div className="panel">
          <div className="panel-hdr"><span className="panel-title">Risk Distribution</span></div>
          <div className="panel-body"><DonutChart stats={stats} /></div>
        </div>
        <div className="panel">
          <div className="panel-hdr"><span className="panel-title">Cost &amp; Savings by Type</span></div>
          <div className="panel-body"><CostChart findings={findings} /></div>
        </div>
        <div className="panel">
          <div className="panel-hdr"><span className="panel-title">Compliance Overview</span></div>
          <div className="panel-body"><ComplianceChart findings={findings} /></div>
        </div>
      </div>

      {/* ── Scoring Methodology ── */}
      <div className="panel methodology-panel">
        <div className="panel-hdr">
          <span className="panel-title">Risk Scoring Methodology</span>
          <span className="method-sub">Transparent, weighted multi-factor formula</span>
        </div>
        <div className="method-body">
          <div className="method-formula">
            <span className="mf-part mf-sec">Security Rules × 4</span>
            <span className="mf-op">+</span>
            <span className="mf-part mf-comp">Compliance × 3</span>
            <span className="mf-op">+</span>
            <span className="mf-part mf-acc">Access × 3</span>
            <span className="mf-op">+</span>
            <span className="mf-part mf-cost">Cost ÷ 5</span>
            <span className="mf-op">+</span>
            <span className="mf-part mf-idle">Idle Penalty</span>
            <span className="mf-op">×</span>
            <span className="mf-part mf-exp">1.5× if Public</span>
            <span className="mf-op">=</span>
            <span className="mf-part mf-result">Risk Score</span>
          </div>
          <div className="method-thresholds">
            {[['CRITICAL','≥ 100','#dc2626'],['HIGH','≥ 60','#ea580c'],['MEDIUM','≥ 30','#d97706'],['LOW','< 30','#16a34a']].map(([p,t,c]) => (
              <span key={p} className="mth-pill" style={{ background: c + '18', color: c, borderColor: c + '44' }}>
                {p} {t}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* ── Findings Table ── */}
      <div className="panel">
        <div className="panel-hdr">
          <span className="panel-title">All Findings</span>
          <div className="filter-tabs">
            {TABS.map(t => (
              <button key={t.k}
                className={`ftab ftab-${t.k.toLowerCase()} ${filter === t.k ? 'active' : ''}`}
                onClick={() => setFilter(t.k)}
              >
                {t.label}
                <span className="ftab-n">{t.n}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="tbl-scroll">
          <table className="tbl">
            <thead>
              <tr>
                <th className="th-rank">#</th>
                <th>Resource</th>
                <th>Type</th>
                <th>Region</th>
                <th>Priority</th>
                <th className="th-r th-sortable" onClick={() => toggleSort('risk_score')}>
                  Risk Score <SortIcon col="risk_score" />
                </th>
                <th className="th-r th-sortable" onClick={() => toggleSort('cost')}>
                  Cost / mo <SortIcon col="cost" />
                </th>
                <th className="th-r th-sortable" onClick={() => toggleSort('savings_potential')}>
                  Savings <SortIcon col="savings_potential" />
                </th>
                <th className="th-r">Issues</th>
                <th className="th-r">Vulns</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((f, idx) => (
                <tr key={f.resource_id}
                  className={selected?.resource_id === f.resource_id ? 'tr-selected' : ''}
                  onClick={() => openDrawer(f)}
                >
                  <td className="td-rank">{idx + 1}</td>
                  <td>
                    <span className="td-id">{f.resource_id}</span>
                    <span className="td-name">{f.resource_name}</span>
                  </td>
                  <td><span className="chip-type">{f.resource_type}</span></td>
                  <td className="td-region">{f.region}</td>
                  <td>
                    <span className="chip-pri" style={{ color: pc(f.priority), background: pc(f.priority) + '18', borderColor: pc(f.priority) + '44' }}>
                      {f.priority}
                    </span>
                  </td>
                  <td className="td-r">
                    <span className="td-score" style={{ color: pc(f.priority) }}>{f.risk_score}</span>
                  </td>
                  <td className="td-r">${f.cost}</td>
                  <td className="td-r td-save">${Math.round(f.savings_potential || 0)}</td>
                  <td className="td-r">{f.issues?.length || 0}</td>
                  <td className="td-r">
                    {f.vuln_count > 0
                      ? <span className="badge-vuln">{f.vuln_count}</span>
                      : <span className="td-dash">—</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Detail Drawer ── */}
      {selected && (
        <>
          <div className={`drawer-overlay ${drawerOpen ? 'open' : ''}`} onClick={closeDrawer} />
          <aside className={`drawer ${drawerOpen ? 'open' : ''}`}>
            <div className="drawer-hdr">
              <div>
                <div className="drawer-id">{selected.resource_id}</div>
                <div className="drawer-name">{selected.resource_name}</div>
              </div>
              <button className="drawer-close" onClick={closeDrawer}>✕</button>
            </div>

            <div className="drawer-body">

              {/* Chips */}
              <div className="drawer-chips">
                <span className="chip-type">{selected.resource_type}</span>
                <span className="chip-region">📍 {selected.region}</span>
                <span className="chip-pri" style={{ color: pc(selected.priority), background: pc(selected.priority) + '18', borderColor: pc(selected.priority) + '44' }}>
                  {selected.priority_tag} {selected.priority}
                </span>
              </div>

              {/* ── Risk Score Breakdown ── */}
              <ScoreBreakdown finding={selected} />

              {/* Key Metrics */}
              <div className="ds">
                <div className="ds-title">Key Metrics</div>
                <div className="kv-grid">
                  {[
                    { k: 'Risk Score',   v: selected.risk_score,                               c: pc(selected.priority) },
                    { k: 'Usage',        v: `${selected.usage}%`,                              c: selected.usage < 5 ? '#dc2626' : '#0f172a' },
                    { k: 'Cost / mo',    v: `$${selected.cost}`,                               c: '#0f172a' },
                    { k: 'Savings',      v: `$${(selected.savings_potential || 0).toFixed(2)}`, c: '#059669' },
                    { k: 'Compliance',   v: `${selected.compliance_score}/100`,                 c: selected.compliance_score >= 80 ? '#16a34a' : selected.compliance_score >= 60 ? '#d97706' : '#dc2626' },
                    { k: 'Rightsizing',  v: selected.rightsizing,                               c: selected.rightsizing === 'terminate' ? '#dc2626' : selected.rightsizing === 'downsize' ? '#ea580c' : '#16a34a' },
                  ].map((m, i) => (
                    <div key={i} className="kv-cell">
                      <span className="kv-key">{m.k}</span>
                      <span className="kv-val" style={{ color: m.c }}>{m.v}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Performance */}
              <div className="ds">
                <div className="ds-title">Performance (CloudWatch)</div>
                <div className="perf-list">
                  {[
                    { l: 'CPU',    v: selected.cpu_avg,          c: '#3b82f6' },
                    { l: 'Memory', v: selected.memory_avg,       c: '#8b5cf6' },
                    { l: 'Disk',   v: selected.disk_utilization, c: '#06b6d4' },
                  ].map(m => (
                    <div key={m.l} className="pf-row">
                      <span className="pf-label">{m.l}</span>
                      <div className="pf-track">
                        <div className="pf-fill" style={{ width: `${Math.min(m.v || 0, 100)}%`, background: m.c }} />
                      </div>
                      <span className="pf-val">{(m.v || 0).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Security Signals */}
              <div className="ds">
                <div className="ds-title">Security Signals (SecurityHub + CloudTrail)</div>
                <div className="sig-grid">
                  {[
                    { l: 'Vulnerabilities', v: `${selected.vuln_count} (${selected.cve_count} CVEs)`, bad: selected.vuln_count > 0 },
                    { l: 'Failed Logins',   v: selected.failed_logins,                                 bad: selected.failed_logins > 5 },
                    { l: 'SSH Exposed',     v: selected.ssh_exposed ? 'YES' : 'No',                   bad: selected.ssh_exposed },
                    { l: 'RDP Exposed',     v: selected.rdp_exposed ? 'YES' : 'No',                   bad: selected.rdp_exposed },
                    { l: 'Last Activity',   v: `${selected.last_activity_days}d ago`,                 bad: selected.last_activity_days > 90 },
                    { l: 'Suspicious API',  v: `${selected.suspicious_api_calls} calls`,              bad: selected.suspicious_api_calls > 0 },
                  ].map((s, i) => (
                    <div key={i} className={`sig-cell ${s.bad ? 'sig-bad' : 'sig-ok'}`}>
                      <span className="sig-dot" />
                      <span className="sig-label">{s.l}</span>
                      <span className="sig-val">{s.v}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Issues */}
              <div className="ds">
                <div className="ds-title">Issues Detected ({selected.issues?.length})</div>
                <div className="issues-list">
                  {(selected.issues || []).map((iss, i) => (
                    <div key={i} className="issue-row">
                      <span className="issue-bullet" />
                      {iss}
                    </div>
                  ))}
                </div>
              </div>

              {/* Compliance Violations */}
              {selected.compliance_violations?.length > 0 && (
                <div className="ds">
                  <div className="ds-title">Compliance Violations ({selected.compliance_violations.length})</div>
                  {selected.compliance_violations.map((v, i) => {
                    const [std, ...rest] = v.split(':');
                    return (
                      <div key={i} className="comp-row">
                        <span className="comp-std">{std.trim()}</span>
                        <span className="comp-desc">{rest.join(':').trim()}</span>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Impact */}
              <div className="ds">
                <div className="ds-title">Risk Impact</div>
                <div className="impact-box">{selected.impact}</div>
              </div>

              {/* Recommendation */}
              <div className="ds">
                <div className="ds-title">Recommended Fix</div>
                <div className="rec-box">{selected.recommendation}</div>
              </div>

              {/* Categories */}
              <div className="ds">
                <div className="ds-title">Categories</div>
                <div className="cats">
                  {(selected.categories || []).map((c, i) => (
                    <span key={i} className="cat-tag">{c}</span>
                  ))}
                </div>
              </div>

              {/* CLI Fix Commands */}
              {selected.cli_fixes && Object.keys(selected.cli_fixes).length > 0 && (
                <div className="ds">
                  <div className="ds-title">AWS CLI Fix Commands</div>
                  <p className="cli-note">
                    Replace <code>&lt;SG_ID&gt;</code>, <code>&lt;ACCOUNT_ID&gt;</code> with your actual values.
                  </p>
                  {Object.entries(selected.cli_fixes).map(([issue, cmds], i) => {
                    const txt = cmds.join('\n');
                    return (
                      <div key={i} className="cli-block">
                        <div className="cli-block-hdr">
                          <span className="cli-issue-label">▸ {issue}</span>
                          <button className={`cli-copy-btn ${copied === issue ? 'copied' : ''}`} onClick={() => copy(issue, txt)}>
                            {copied === issue ? '✓ Copied' : 'Copy'}
                          </button>
                        </div>
                        <pre className="cli-pre">{txt}</pre>
                      </div>
                    );
                  })}
                </div>
              )}

            </div>
          </aside>
        </>
      )}

    </div>
  );
}
