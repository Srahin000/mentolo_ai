/**
 * HoloMentor Mobile - Modular API Service
 * Reusable API functions for React Native and future Unity integration
 */

import config from './config';

const API_BASE_URL = config.API_BASE_URL;

/**
 * Ask a question to the AI assistant
 * @param {string} userInput - The user's question/input
 * @param {string} userId - Optional user ID
 * @param {object} context - Optional context object
 * @returns {Promise<{text: string, audio_url: string, emotion: string}>}
 */
export async function askQuestion(userInput, userId = null, context = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_input: userInput,
        user_id: userId,
        context: context,
      }),
      timeout: config.TIMEOUT,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return {
      text: data.text,
      audio_url: data.audio_url,
      emotion: data.emotion,
      response_time: data.response_time,
      audio_duration: data.audio_duration,
    };
  } catch (error) {
    console.error('Error asking question:', error);
    throw error;
  }
}

/**
 * Play audio from URL
 * This function is platform-agnostic and can be used by React Native or Unity
 * @param {string} audioUrl - URL of the audio file
 * @returns {Promise<void>}
 */
export async function playAudio(audioUrl) {
  // This is a placeholder - actual implementation depends on platform
  // React Native: Use expo-av
  // Unity: Use UnityWebRequest or AudioSource
  console.log('Playing audio from:', audioUrl);
  
  // For React Native, this will be implemented in the component
  // For Unity, this will be implemented in C# script
  return audioUrl;
}

/**
 * Check backend health
 * @returns {Promise<boolean>}
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL.replace('/ask', '')}/health`, {
      method: 'GET',
      timeout: 5000,
    });

    if (!response.ok) {
      return false;
    }

    const data = await response.json();
    return data.status === 'healthy';
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
}

/**
 * Generate a lesson plan
 * @param {string} topic - Topic for the lesson
 * @param {string} planType - 'lesson', 'quiz', or 'curriculum'
 * @param {string} userId - Optional user ID
 * @param {object} parameters - Optional parameters
 * @returns {Promise<object>}
 */
export async function generatePlan(topic, planType = 'lesson', userId = null, parameters = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}/plan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        topic: topic,
        plan_type: planType,
        user_id: userId,
        parameters: parameters,
      }),
      timeout: config.TIMEOUT,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error generating plan:', error);
    throw error;
  }
}

// Export all functions for easy importing
export default {
  askQuestion,
  playAudio,
  checkHealth,
  generatePlan,
};

