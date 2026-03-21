import { useState, useRef, useEffect } from 'react';
import './Copilot.css';

// ── Markdown-lite renderer ────────────────────────────────────────────────────
const Render = ({ text }) => {
  const parts = text.split(/(```[\s\S]*?```)/g);

  return (
    <div className="render">
      {parts.map((part, i) => {
        // Code block
        if (part.startsWith('```')) {
          const body = part.replace(/^```[a-z]*\n?/, '').replace(/\n?```$/, '');
          return (
            <div key={i} className="r-code">
              <pre><code>{body}</code></pre>
            </div>
          );
        }

        // Regular text
        return (
          <div key={i}>
            {part.split('\n').map((line, j) => {
              if (!line.trim()) return null;

              // Section header: **ALL CAPS**
              if (/^\*\*[A-Z][A-Z\s—\-]+\*\*$/.test(line.trim())) {
                return <div key={j} className="r-section">{line.replace(/\*\*/g, '')}</div>;
              }

              // Table separator
              if (/^\|[\-|\s]+\|$/.test(line.trim())) return null;

              // Table row
              if (line.trim().startsWith('|')) {
                const cells = line.split('|').filter(Boolean).map(c => c.trim());
                return (
                  <div key={j} className="r-tr">
                    {cells.map((c, k) => (
                      <span key={k} className="r-td"
                        dangerouslySetInnerHTML={{ __html: c.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }}
                      />
                    ))}
                  </div>
                );
              }

              // List item
              if (line.trim().startsWith('- ') || line.trim().startsWith('• ')) {
                const content = line.replace(/^[-•]\s+/, '');
                const html    = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/`([^`]+)`/g, '<code>$1</code>');
                return <div key={j} className="r-li" dangerouslySetInnerHTML={{ __html: '● ' + html }} />;
              }

              // Numbered list
              if (/^\d+\.\s/.test(line.trim())) {
                const html = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/`([^`]+)`/g, '<code>$1</code>');
                return <div key={j} className="r-li" dangerouslySetInnerHTML={{ __html: html }} />;
              }

              // Normal paragraph
              const html = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/`([^`]+)`/g, '<code>$1</code>');
              return <p key={j} dangerouslySetInnerHTML={{ __html: html }} />;
            })}
          </div>
        );
      })}
    </div>
  );
};

// ── Quick Commands ────────────────────────────────────────────────────────────
const CMDS = [
  { cmd: 'summary',          label: 'Executive Summary',  desc: 'Full risk & cost report'   },
  { cmd: 'show critical',    label: 'Critical Findings',  desc: 'CRITICAL priority only'     },
  { cmd: 'show high',        label: 'High Findings',      desc: 'HIGH priority resources'    },
  { cmd: 'show cost issues', label: 'Cost Optimization',  desc: 'Savings & rightsizing ops'  },
  { cmd: 'show security',    label: 'Security Issues',    desc: 'Threats & misconfigs'       },
  { cmd: 'explain r1',       label: 'Explain Resource',   desc: 'Deep dive on r1'            },
  { cmd: 'fix r1',           label: 'Get Fix Commands',   desc: 'AWS CLI for r1'             },
];

// ── Copilot ───────────────────────────────────────────────────────────────────
export default function Copilot() {
  const [query,    setQuery]    = useState('');
  const [messages, setMessages] = useState([{
    type: 'bot',
    content: `**WELCOME TO GENAI CLOUD SECURITY COPILOT**

Powered by **Gemini AI** — I can help you analyze your cloud security posture, identify risks, and generate fix commands.

**What I can do:**
- Explain why specific resources are flagged as CRITICAL or HIGH risk
- Generate AWS CLI commands to remediate security misconfigurations
- Summarize your entire cloud cost and security exposure
- Identify savings opportunities and rightsizing recommendations

Use the quick commands on the left, or type freely below.`,
  }]);
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const send = async (q) => {
    const text = (q ?? query).trim();
    if (!text) return;
    setMessages(m => [...m, { type: 'user', content: text }]);
    setQuery('');
    setLoading(true);
    try {
      const res  = await fetch('http://localhost:5000/api/copilot', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ query: text }),
      });
      const data = await res.json();
      setMessages(m => [...m, { type: 'bot', content: data.response }]);
    } catch {
      setMessages(m => [...m, { type: 'error', content: 'Connection failed. Make sure the backend is running on port 5000.' }]);
    } finally {
      setLoading(false);
    }
  };

  const onKey = e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } };

  return (
    <div className="copilot">

      {/* ── Left Panel ── */}
      <div className="cp-left">
        <div className="cp-left-hdr">
          <div className="cp-ai-badge">
            <span className="cp-ai-dot" />
            <span>Gemini AI · Active</span>
          </div>
          <div className="cp-left-title">Quick Commands</div>
        </div>

        <div className="cp-cmd-list">
          {CMDS.map((c, i) => (
            <button key={i} className="cp-cmd" onClick={() => send(c.cmd)} disabled={loading}>
              <span className="cp-cmd-label">{c.label}</span>
              <span className="cp-cmd-desc">{c.desc}</span>
            </button>
          ))}
        </div>

        <div className="cp-hint-box">
          <div className="cp-hint-title">Resource IDs</div>
          <div className="cp-hint-body">
            Reference resources by ID — e.g. <code>explain r5</code> or <code>fix r12</code>
          </div>
        </div>
      </div>

      {/* ── Chat Area ── */}
      <div className="cp-chat">
        <div className="cp-chat-hdr">
          <div className="cp-chat-title">
            <span className="cp-chat-icon">◈</span>
            GenAI Copilot
          </div>
          <div className="cp-chat-sub">Cloud Security &amp; FinOps Assistant</div>
        </div>

        <div className="cp-msgs">
          {messages.map((m, i) => (
            <div key={i} className={`cp-msg cp-msg-${m.type}`}>
              {m.type !== 'user' && (
                <div className={`cp-avatar ${m.type === 'error' ? 'cp-avatar-err' : ''}`}>
                  {m.type === 'bot' ? '◈' : '⚠'}
                </div>
              )}
              <div className="cp-bubble">
                {m.type === 'bot'
                  ? <Render text={m.content} />
                  : <p>{m.content}</p>
                }
              </div>
              {m.type === 'user' && (
                <div className="cp-avatar cp-avatar-user">AP</div>
              )}
            </div>
          ))}

          {loading && (
            <div className="cp-msg cp-msg-bot">
              <div className="cp-avatar">◈</div>
              <div className="cp-bubble">
                <div className="cp-typing"><span /><span /><span /></div>
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        <form className="cp-input-row" onSubmit={e => { e.preventDefault(); send(); }}>
          <input
            className="cp-input"
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={onKey}
            placeholder="Ask about findings, risks, fixes… e.g. 'fix r3' or 'show critical'"
            disabled={loading}
            autoFocus
          />
          <button className="cp-send" type="submit" disabled={loading || !query.trim()}>↑</button>
        </form>
      </div>

    </div>
  );
}
