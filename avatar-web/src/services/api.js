/**
 * API Service for HeyGen Avatar Web App
 * Connects to backend API
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
 * Create HeyGen realtime avatar session
 */
export async function createHeyGenSession(data) {
  try {
    const response = await api.post('/heygen/session/create', data);
    return response.data;
  } catch (error) {
    console.error('Error creating HeyGen session:', error);
    throw error;
  }
}

/**
 * Get available HeyGen avatars
 */
export async function getHeyGenAvatars() {
  try {
    const response = await api.get('/heygen/avatars');
    return response.data;
  } catch (error) {
    console.error('Error fetching avatars:', error);
    throw error;
  }
}

/**
 * Send WebRTC answer SDP to complete HeyGen streaming session
 */
export async function answerHeyGenSession(sessionId, sdpAnswer) {
  try {
    const response = await api.post('/heygen/session/answer', {
      session_id: sessionId,
      sdp: sdpAnswer
    });
    return response.data;
  } catch (error) {
    console.error('Error sending WebRTC answer:', error);
    throw error;
  }
}

/**
 * Get available HeyGen voices
 */
export async function getHeyGenVoices() {
  try {
    const response = await api.get('/heygen/voices');
    return response.data;
  } catch (error) {
    console.error('Error fetching voices:', error);
    throw error;
  }
}

/**
 * Test HeyGen connection
 */
export async function testHeyGen() {
  try {
    const response = await api.get('/heygen/test');
    return response.data;
  } catch (error) {
    console.error('Error testing HeyGen:', error);
    throw error;
  }
}

/**
 * Close/terminate a HeyGen streaming session
 */
export async function closeHeyGenSession(sessionId) {
  try {
    const response = await api.post('/heygen/session/close', {
      session_id: sessionId
    });
    return response.data;
  } catch (error) {
    console.error('Error closing HeyGen session:', error);
    throw error;
  }
}

export default {
  createHeyGenSession,
  getHeyGenAvatars,
  getHeyGenVoices,
  testHeyGen,
  answerHeyGenSession,
  closeHeyGenSession,
};

