import { useState } from 'react';
import Dashboard from './Dashboard';
import Copilot   from './Copilot';
import './App.css';

const NAV = [
  { id: 'dashboard', icon: '▦', label: 'Security Overview' },
  { id: 'copilot',   icon: '◈', label: 'GenAI Copilot',    badge: 'AI' },
];

const CLOUDS = [
  { id: 'aws',   label: 'AWS',   icon: '☁' },
  { id: 'azure', label: 'Azure', icon: '◇' },
  { id: 'gcp',   label: 'GCP',   icon: '◆' },
];

export default function App() {
  const [page,      setPage]      = useState('dashboard');
  const [cloud,     setCloud]     = useState('aws');
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className={`shell ${collapsed ? 'sb-collapsed' : ''}`}>

      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="sb-brand">
          <span className="sb-logo">⬡</span>
          {!collapsed && (
            <div className="sb-brand-text">
              <div className="sb-name">CloudCopilot</div>
              <div className="sb-tagline">Security &amp; FinOps</div>
            </div>
          )}
        </div>

        <div className="sb-divider" />

        <nav className="sb-nav">
          {!collapsed && <div className="sb-section-label">WORKSPACE</div>}
          {NAV.map(n => (
            <button
              key={n.id}
              className={`sb-item ${page === n.id ? 'active' : ''}`}
              onClick={() => setPage(n.id)}
              title={collapsed ? n.label : undefined}
            >
              <span className="sb-item-icon">{n.icon}</span>
              {!collapsed && (
                <>
                  <span className="sb-item-label">{n.label}</span>
                  {n.badge && <span className="sb-badge">{n.badge}</span>}
                </>
              )}
            </button>
          ))}
        </nav>

        <div className="sb-footer">
          <div className="ai-pill">
            <span className="ai-dot" />
            {!collapsed && <span className="ai-label">Gemini AI · Active</span>}
          </div>
        </div>
      </aside>

      {/* ── Main ── */}
      <div className="main-area">

        {/* Top Bar */}
        <header className="topbar">
          <button className="menu-btn" onClick={() => setCollapsed(c => !c)} aria-label="Toggle sidebar">
            <span /><span /><span />
          </button>

          <nav className="breadcrumb">
            <span className="bc-root">Console</span>
            <span className="bc-sep">›</span>
            <span className="bc-seg">Security</span>
            <span className="bc-sep">›</span>
            <span className="bc-cur">
              {page === 'dashboard' ? 'Overview' : 'GenAI Copilot'}
            </span>
          </nav>

          <div className="topbar-right">
            <div className="region-pill">
              <span className="region-dot" />
              us-east-1
            </div>
            <div className="user-avatar" title="Aditya Patil">AP</div>
          </div>
        </header>

        {/* Page Content */}
        <main className="page-content">
          {page === 'dashboard' ? <Dashboard cloud={cloud} /> : <Copilot cloud={cloud} />}
        </main>

        {/* Cloud Selector */}
        {page === 'dashboard' && (
          <div className="cloud-selector">
            {CLOUDS.map(c => (
              <button
                key={c.id}
                className={`cloud-btn ${cloud === c.id ? 'active' : ''}`}
                onClick={() => setCloud(c.id)}
                title={c.label}
              >
                <span className="cloud-icon">{c.icon}</span>
                <span className="cloud-label">{c.label}</span>
              </button>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}
