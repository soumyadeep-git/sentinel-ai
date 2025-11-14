import React, { useState, useEffect, useRef } from 'react';
import { startInvestigation, getInvestigationStatus } from './api';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [investigation, setInvestigation] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const intervalRef = useRef(null);

  useEffect(() => {
    // Clear any existing interval when the component unmounts or the investigation changes
    return () => clearInterval(intervalRef.current);
  }, []);

  useEffect(() => {
    // This effect handles polling for results
    if (investigation && (investigation.status === 'PENDING' || investigation.status === 'IN_PROGRESS')) {
      intervalRef.current = setInterval(async () => {
        try {
          const response = await getInvestigationStatus(investigation.id);
          setInvestigation(response.data);
          if (response.data.status === 'COMPLETED' || response.data.status === 'FAILED') {
            clearInterval(intervalRef.current);
            setIsLoading(false);
          }
        } catch (err) {
          setError('Failed to fetch investigation status.');
          setIsLoading(false);
          clearInterval(intervalRef.current);
        }
      }, 3000); // Poll every 3 seconds
    }
  }, [investigation]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      setError('Query cannot be empty.');
      return;
    }
    // Clear previous polling interval before starting a new one
    clearInterval(intervalRef.current);
    
    setIsLoading(true);
    setError('');
    setInvestigation(null); // Clear previous results

    try {
      const response = await startInvestigation(query);
      setInvestigation(response.data);
    } catch (err) {
      setError('Failed to start investigation. Is the backend running?');
      setIsLoading(false);
    }
  };

  const renderStatus = (status) => {
    let color = '';
    switch (status) {
      case 'PENDING': color = '#f0ad4e'; break;
      case 'IN_PROGRESS': color = '#0275d8'; break;
      case 'COMPLETED': color = '#5cb85c'; break;
      case 'FAILED': color = '#d9534f'; break;
      default: color = '#6c757d';
    }
    return <strong style={{ color }}>{status}</strong>;
  };

  return (
    <div className="container">
      <header>
        <h1>Sentinel AI</h1>
        <p>Agentic Security Log Analysis Copilot</p>
      </header>
      
      <div className="form-container">
        <form onSubmit={handleSubmit}>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your security query (e.g., 'Show me all failed login attempts or errors')"
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Investigating...' : 'Start Investigation'}
          </button>
        </form>
      </div>

      {error && <div className="error-box">{error}</div>}

      {investigation && (
        <div className="results-container">
          <h2>Investigation Details</h2>
          <div className="details-box">
            <p><strong>ID:</strong> {investigation.id}</p>
            <p><strong>Query:</strong> {investigation.query}</p>
            <p><strong>Status:</strong> {renderStatus(investigation.status)}</p>
          </div>
          
          {(investigation.status === 'COMPLETED' || investigation.status === 'FAILED') && (
            <div className="summary-box">
              <h3>AI Summary</h3>
              <pre>{investigation.summary || 'No summary was generated.'}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;