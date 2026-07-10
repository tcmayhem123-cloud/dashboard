import React, { useState, useEffect } from 'react';
import GptInsights from './components/GptInsights';
import OtherToolInsights from './components/OtherToolInsights';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

export default function App() {
  const [tools, setTools] = useState([]);
  const [selectedTool, setSelectedTool] = useState('gpt_tool');
  const [insightsData, setInsightsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dbStatus, setDbStatus] = useState({ connected: false, type: '' });

  // 1. Fetch available tools list
  useEffect(() => {
    fetch(`${API_BASE_URL}/tools`)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load tools catalog');
        return res.json();
      })
      .then((data) => {
        setTools(data);
      })
      .catch((err) => {
        console.error(err);
        setError('Connection to backend could not be established. Make sure the backend server is running on port 8000.');
      });

    // Check DB Status
    fetch(`${API_BASE_URL}/status`)
      .then((res) => res.json())
      .then((data) => {
        setDbStatus({
          connected: data.status === 'online',
          type: data.database === 'real_mongodb' ? 'MongoDB (Real)' : 'MongoDB (Mock In-Memory)'
        });
      })
      .catch((err) => {
        console.error(err);
        setDbStatus({ connected: false, type: 'Disconnected' });
      });
  }, []);

  // 2. Fetch insights data whenever selected tool changes
  useEffect(() => {
    if (!selectedTool) return;
    setLoading(true);
    setError(null); // Clear previous errors
    fetch(`${API_BASE_URL}/insights/${selectedTool}`)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch tool insights');
        return res.json();
      })
      .then((data) => {
        setInsightsData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError('Error loading data for the selected tool.');
        setLoading(false);
      });
  }, [selectedTool]);

  const handleToolChange = (e) => {
    const nextTool = e.target.value;
    setSelectedTool(nextTool);
    setInsightsData(null); // Clear old data to prevent cross-tool rendering crashes
    setLoading(true);
  };

  return (
    <div className="app-container">
      {/* Top Header */}
      <header className="app-header">
        <div className="brand-section">
          <h1>AI Tools Suite Analytics</h1>
          <p>Real-time analytics platform and metrics dashboard</p>
        </div>

        <div className="controls-section">
          {dbStatus.connected && (
            <div className="status-indicator">
              Database: {dbStatus.type}
            </div>
          )}
          <label htmlFor="tool-select">Select Module:</label>
          <div className="dropdown-container">
            <select
              id="tool-select"
              className="dropdown-select"
              value={selectedTool}
              onChange={handleToolChange}
            >
              {tools.map((t) => (
                <option key={t.key} value={t.key}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="app-content">
        {error && (
          <div className="chart-card glass" style={{ borderColor: '#ef4444', padding: '2rem', textAlign: 'center' }}>
            <h3 style={{ color: '#ef4444', marginBottom: '0.5rem' }}>Connection Alert</h3>
            <p style={{ color: '#9ca3af' }}>{error}</p>
            <button 
              onClick={() => window.location.reload()} 
              style={{
                marginTop: '1.25rem',
                padding: '0.6rem 1.25rem',
                backgroundColor: '#8b5cf6',
                border: 'none',
                color: '#fff',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '600'
              }}
            >
              Retry Connection
            </button>
          </div>
        )}

        {!error && loading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <div className="loading-text">Loading insights dashboard...</div>
          </div>
        )}

        {!error && !loading && selectedTool === 'gpt_tool' && (
          <GptInsights data={insightsData} />
        )}

        {!error && !loading && selectedTool !== 'gpt_tool' && (
          <OtherToolInsights toolKey={selectedTool} data={insightsData} />
        )}
      </main>
    </div>
  );
}
