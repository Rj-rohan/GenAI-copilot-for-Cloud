import { useState, useEffect } from 'react';
import './Dashboard.css';

const Dashboard = () => {
  const [findings, setFindings] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    totalCost: 0
  });
  const [selectedPriority, setSelectedPriority] = useState('ALL');
  const [selectedResource, setSelectedResource] = useState(null);

  useEffect(() => {
    loadFindings();
  }, []);

  const loadFindings = async () => {
    try {
      const response = await fetch('/findings.json');
      const data = await response.json();
      setFindings(data);
      calculateStats(data);
    } catch (error) {
      console.error('Error loading findings:', error);
    }
  };

  const calculateStats = (data) => {
    const stats = {
      total: data.length,
      critical: data.filter(f => f.priority === 'CRITICAL').length,
      high: data.filter(f => f.priority === 'HIGH').length,
      medium: data.filter(f => f.priority === 'MEDIUM').length,
      low: data.filter(f => f.priority === 'LOW').length,
      totalCost: data.reduce((sum, f) => sum + f.cost, 0)
    };
    setStats(stats);
  };

  const filteredFindings = selectedPriority === 'ALL' 
    ? findings 
    : findings.filter(f => f.priority === selectedPriority);

  const getPriorityColor = (priority) => {
    const colors = {
      CRITICAL: '#dc2626',
      HIGH: '#ea580c',
      MEDIUM: '#eab308',
      LOW: '#22c55e'
    };
    return colors[priority] || '#6b7280';
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>🛡️ GenAI Cloud Security Copilot</h1>
        <p>Risk & Cost Optimization Advisor</p>
      </header>

      <div className="stats-grid">
        <div className="stat-card total">
          <div className="stat-value">{stats.total}</div>
          <div className="stat-label">Total Issues</div>
        </div>
        <div className="stat-card critical">
          <div className="stat-value">{stats.critical}</div>
          <div className="stat-label">Critical</div>
        </div>
        <div className="stat-card high">
          <div className="stat-value">{stats.high}</div>
          <div className="stat-label">High</div>
        </div>
        <div className="stat-card medium">
          <div className="stat-value">{stats.medium}</div>
          <div className="stat-label">Medium</div>
        </div>
        <div className="stat-card low">
          <div className="stat-value">{stats.low}</div>
          <div className="stat-label">Low</div>
        </div>
        <div className="stat-card cost">
          <div className="stat-value">${stats.totalCost}</div>
          <div className="stat-label">Cost at Risk</div>
        </div>
      </div>

      <div className="filters">
        <button 
          className={selectedPriority === 'ALL' ? 'active' : ''}
          onClick={() => setSelectedPriority('ALL')}
        >
          All
        </button>
        <button 
          className={selectedPriority === 'CRITICAL' ? 'active' : ''}
          onClick={() => setSelectedPriority('CRITICAL')}
        >
          Critical
        </button>
        <button 
          className={selectedPriority === 'HIGH' ? 'active' : ''}
          onClick={() => setSelectedPriority('HIGH')}
        >
          High
        </button>
        <button 
          className={selectedPriority === 'MEDIUM' ? 'active' : ''}
          onClick={() => setSelectedPriority('MEDIUM')}
        >
          Medium
        </button>
        <button 
          className={selectedPriority === 'LOW' ? 'active' : ''}
          onClick={() => setSelectedPriority('LOW')}
        >
          Low
        </button>
      </div>

      <div className="findings-container">
        <div className="findings-list">
          <h2>Findings ({filteredFindings.length})</h2>
          {filteredFindings.map((finding) => (
            <div 
              key={finding.resource_id} 
              className="finding-card"
              onClick={() => setSelectedResource(finding)}
              style={{ borderLeftColor: getPriorityColor(finding.priority) }}
            >
              <div className="finding-header">
                <span className="resource-id">{finding.resource_id}</span>
                <span className="resource-type">{finding.resource_type}</span>
                <span 
                  className="priority-badge"
                  style={{ backgroundColor: getPriorityColor(finding.priority) }}
                >
                  {finding.priority}
                </span>
              </div>
              <div className="finding-summary">{finding.summary}</div>
              <div className="finding-meta">
                <span>Risk Score: {finding.risk_score}</span>
                <span>Cost: ${finding.cost}/mo</span>
              </div>
            </div>
          ))}
        </div>

        {selectedResource && (
          <div className="finding-details">
            <div className="details-header">
              <h2>Resource Details</h2>
              <button onClick={() => setSelectedResource(null)}>✕</button>
            </div>
            
            <div className="detail-section">
              <h3>{selectedResource.resource_id} ({selectedResource.resource_type})</h3>
              <div 
                className="priority-badge large"
                style={{ backgroundColor: getPriorityColor(selectedResource.priority) }}
              >
                {selectedResource.priority_tag} {selectedResource.priority}
              </div>
            </div>

            <div className="detail-section">
              <h4>Summary</h4>
              <p>{selectedResource.summary}</p>
            </div>

            <div className="detail-section">
              <h4>Impact</h4>
              <p className="impact-text">{selectedResource.impact}</p>
            </div>

            <div className="detail-section">
              <h4>Issues Found</h4>
              <ul className="issues-list">
                {selectedResource.issues.map((issue, idx) => (
                  <li key={idx}>{issue}</li>
                ))}
              </ul>
            </div>

            <div className="detail-section">
              <h4>Recommendations</h4>
              <div className="recommendation-box">
                {selectedResource.recommendation}
              </div>
            </div>

            <div className="detail-section">
              <h4>Metrics</h4>
              <div className="metrics-grid">
                <div className="metric">
                  <span className="metric-label">Risk Score</span>
                  <span className="metric-value">{selectedResource.risk_score}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Usage</span>
                  <span className="metric-value">{selectedResource.usage}%</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Cost</span>
                  <span className="metric-value">${selectedResource.cost}/mo</span>
                </div>
              </div>
            </div>

            <div className="detail-section">
              <h4>Categories</h4>
              <div className="categories">
                {selectedResource.categories.map((cat, idx) => (
                  <span key={idx} className="category-tag">{cat}</span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
