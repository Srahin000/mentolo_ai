/**
 * API Service for MENTOLO AI Dashboard
 * Handles all backend communication
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Get child profile with development insights
 */
export async function getChildProfile(childId) {
  try {
    const response = await api.get(`/child-profile/${childId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching child profile:', error);
    throw error;
  }
}

/**
 * Get dashboard data
 */
export async function getDashboard(userId, days = 30) {
  try {
    const response = await api.get('/dashboard', {
      params: { user_id: userId, days },
      headers: { 'X-User-ID': userId },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard:', error);
    throw error;
  }
}

/**
 * Get analytics insights
 */
export async function getAnalyticsInsights(userId, days = 30) {
  try {
    const response = await api.get('/analytics/insights', {
      params: { user_id: userId, days },
      headers: { 'X-User-ID': userId },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching analytics insights:', error);
    throw error;
  }
}

/**
 * Get coaching center recommendations
 */
export async function getCoachingCenters(userId, radius = 10000) {
  try {
    const response = await api.get('/recommendations/coaching-centers', {
      params: { user_id: userId, radius },
      headers: { 'X-User-ID': userId },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching coaching centers:', error);
    // Return a structured error response instead of throwing
    if (error.response) {
      return {
        success: false,
        error: error.response.data?.error || 'Failed to load recommendations',
        message: error.response.data?.message || error.message
      };
    }
    throw error;
  }
}

/**
 * Ask a question to the AI assistant
 */
export async function askQuestion(userInput, userId = null) {
  try {
    const response = await api.post('/ask', {
      user_input: userInput,
      user_id: userId,
    });
    return response.data;
  } catch (error) {
    console.error('Error asking question:', error);
    throw error;
  }
}

/**
 * Get Cortex AI analysis (trends, patterns, benchmarks)
 */
export async function getCortexAnalysis(childId, analysisType = 'trends', days = 90) {
  try {
    const response = await api.post('/cortex/analyze', {
      child_id: childId,
      analysis_type: analysisType,
      days: days,
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching Cortex analysis:', error);
    // Return structured error instead of throwing
    if (error.response) {
      return {
        available: false,
        message: error.response.data?.message || 'Cortex analysis unavailable',
        fallback: error.response.data?.fallback || 'gemini_pro'
      };
    }
    throw error;
  }
}

/**
 * Query Cortex Analyst with natural language question
 */
export async function queryCortexAnalyst(childId, question) {
  try {
    const response = await api.post('/cortex/query', {
      child_id: childId,
      question: question,
    });
    return response.data;
  } catch (error) {
    console.error('Error querying Cortex Analyst:', error);
    // Return structured error instead of throwing
    if (error.response) {
      return {
        available: false,
        message: error.response.data?.message || 'Cortex Analyst unavailable'
      };
    }
    throw error;
  }
}

export default {
  getChildProfile,
  getDashboard,
  getAnalyticsInsights,
  getCoachingCenters,
  askQuestion,
  getCortexAnalysis,
  queryCortexAnalyst,
};

