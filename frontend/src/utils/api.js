/**
 * API utilities for NeuroVision frontend
 * Handles HTTP requests to the backend REST API
 */

const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Generic API request handler with error handling
 * 
 * @param {string} endpoint - API endpoint path (e.g., '/api/status')
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} Response data
 */
export const apiRequest = async (endpoint, options = {}) => {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

/**
 * Get API status
 * 
 * @returns {Promise<Object>} Status information
 */
export const getApiStatus = () => {
  return apiRequest('/status');
};

/**
 * Get recent health events
 * 
 * @param {number} minutes - Time window in minutes
 * @param {number} limit - Maximum events to retrieve
 * @returns {Promise<Array>} List of health events
 */
export const getHealthEvents = (minutes = 5, limit = 100) => {
  return apiRequest(`/api/health-events?minutes=${minutes}&limit=${limit}`);
};

/**
 * Get recent alerts
 * 
 * @param {number} minutes - Time window in minutes
 * @param {number} limit - Maximum alerts to retrieve
 * @returns {Promise<Array>} List of alerts
 */
export const getAlerts = (minutes = 10, limit = 50) => {
  return apiRequest(`/api/alerts?minutes=${minutes}&limit=${limit}`);
};

/**
 * Get health summary statistics
 * 
 * @param {number} minutes - Time window in minutes
 * @returns {Promise<Object>} Summary statistics
 */
export const getHealthSummary = (minutes = 5) => {
  return apiRequest(`/api/health-summary?minutes=${minutes}`);
};

/**
 * Get WebSocket streaming statistics
 * 
 * @returns {Promise<Object>} Stream statistics
 */
export const getStreamStats = () => {
  return apiRequest('/ws/stats');
};

export default {
  apiRequest,
  getApiStatus,
  getHealthEvents,
  getAlerts,
  getHealthSummary,
  getStreamStats
};
