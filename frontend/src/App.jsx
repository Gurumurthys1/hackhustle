import React, { useState } from 'react';
import ReviewDashboard from './components/ReviewDashboard';
import DefectedItemsView from './components/DefectedItemsView';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('returns'); 
  const [selectedClaim, setSelectedClaim] = useState(null);

  const startVerificationFromReturn = (claim) => {
    setSelectedClaim(claim);
    setActiveTab('fraud');
  };

  return (
    <div className="app-layout">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <span style={{color: '#fff'}}>Tri</span>Netra AI
        </div>
        
        <nav className="nav-menu">
          <div 
            className={`nav-item ${activeTab === 'returns' ? 'active' : ''}`}
            onClick={() => setActiveTab('returns')}
          >
            <span className="icon">📦</span> Defected Items
          </div>
          
          <div 
            className={`nav-item ${activeTab === 'fraud' ? 'active' : ''}`}
            onClick={() => setActiveTab('fraud')}
          >
            <span className="icon">🛡️</span> Fraud Console
          </div>
          
          <div className="nav-item">
            <span className="icon">📊</span> Analytics
          </div>
          
          <div className="nav-item">
            <span className="icon">⚙️</span> Settings
          </div>
        </nav>
      </aside>

      {/* Main Dashboard Area */}
      <main className="main-content">
        {activeTab === 'returns' && (
          <DefectedItemsView onInitiateVerification={startVerificationFromReturn} />
        )}
        {activeTab === 'fraud' && (
          <ReviewDashboard 
            initialClaim={selectedClaim} 
            onReset={() => setSelectedClaim(null)} 
          />
        )}
      </main>
    </div>
  );
}

export default App;
