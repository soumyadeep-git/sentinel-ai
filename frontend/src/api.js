import axios from 'axios';

// Prefer env override; default to localhost for host dev, 'api' for Docker
const defaultBase =
  (typeof window !== 'undefined' && window.location.hostname === 'localhost')
    ? 'http://localhost:8000'
    : 'http://api:8000';

const baseURL = process.env.REACT_APP_API_BASE_URL || defaultBase;

const apiClient = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
});

export const startInvestigation = (query) =>
  apiClient.post('/investigate', { query });

export const getInvestigationStatus = (id) =>
  apiClient.get(`/investigations/${id}`);