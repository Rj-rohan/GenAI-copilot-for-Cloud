import { useState } from 'react';
import Dashboard from './Dashboard';
import Copilot   from './Copilot';
import './App.css';

const NAV = [
  { id: 'dashboard', icon: '▦', label: 'Security Overview' },
  { id: 'copilot',   icon: '◈', label: 'GenAI Copilot',    badge: 'AI' },
];

export default function App() {
  const [page,      setPage]      = useState('dashboard');
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
          {page === 'dashboard' ? <Dashboard /> : <Copilot />}
        </main>

      </div>
    </div>
  );
}
