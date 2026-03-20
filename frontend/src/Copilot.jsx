import { useState } from 'react';
import './Copilot.css';

const Copilot = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    {
      type: 'system',
      content: '🤖 Welcome to Cloud Security Copilot! Ask me about your findings, risks, or get recommendations.'
    }
  ]);
  const [loading, setLoading] = useState(false);

  const quickCommands = [
    'show critical',
    'explain r3',
    'summary',
    'show cost issues'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage = { type: 'user', content: query };
    setMessages(prev => [...prev, userMessage]);
    setQuery('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/copilot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });

      const data = await response.json();
      
      const botMessage = {
        type: 'bot',
        content: data.response,
        queryType: data.query_type
      };
      
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        type: 'error',
        content: 'Failed to connect to copilot. Make sure the backend is running on port 5000.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickCommand = (command) => {
    setQuery(command);
  };

  return (
    <div className="copilot-container">
      <div className="copilot-header">
        <h2>🤖 AI Copilot</h2>
        <p>Ask questions about your cloud security findings</p>
      </div>

      <div className="quick-commands">
        <span>Quick commands:</span>
        {quickCommands.map((cmd, idx) => (
          <button
            key={idx}
            onClick={() => handleQuickCommand(cmd)}
            className="quick-cmd-btn"
          >
            {cmd}
          </button>
        ))}
      </div>

      <div className="messages-container">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.type}`}>
            <div className="message-content">
              {msg.content.split('\n').map((line, i) => (
                <p key={i}>{line}</p>
              ))}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message bot">
            <div className="message-content loading">
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="copilot-input">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about findings, risks, or get recommendations..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !query.trim()}>
          Send
        </button>
      </form>
    </div>
  );
};

export default Copilot;
