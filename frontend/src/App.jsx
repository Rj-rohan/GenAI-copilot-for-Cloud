import { useState } from 'react';
import Dashboard from './Dashboard'
import Copilot from './Copilot'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="app">
      <nav className="app-nav">
        <div className="nav-brand">🛡️ Cloud Security Copilot</div>
        <div className="nav-tabs">
          <button 
            className={activeTab === 'dashboard' ? 'active' : ''}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
          <button 
            className={activeTab === 'copilot' ? 'active' : ''}
            onClick={() => setActiveTab('copilot')}
          >
            AI Copilot
          </button>
        </div>
      </nav>
      
      <main className="app-content">
        {activeTab === 'dashboard' ? <Dashboard /> : <Copilot />}
      </main>
    </div>
  )
}

export default App
