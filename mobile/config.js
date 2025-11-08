/**
 * HoloMentor Mobile - Configuration
 * Update API_BASE_URL with your backend server address
 */

// For local development (same device or emulator)
// const API_BASE_URL = 'http://localhost:5000/api';

// For physical device on same WiFi network
// Replace with your computer's IP address (e.g., 192.168.1.100)
// Find your IP: Mac/Linux: ifconfig | grep "inet " | grep -v 127.0.0.1
//              Windows: ipconfig | findstr IPv4
const API_BASE_URL = 'http://YOUR_IP_ADDRESS:5000/api';

// For production/deployed backend
// const API_BASE_URL = 'https://your-backend-domain.com/api';

// Picovoice Configuration
// Get your access key from: https://console.picovoice.ai/
const PICOVOICE_ACCESS_KEY = 'YOUR_PICOVOICE_ACCESS_KEY';

export const getConfig = () => ({
  API_BASE_URL,
  PICOVOICE_ACCESS_KEY: process.env.PICOVOICE_ACCESS_KEY || PICOVOICE_ACCESS_KEY,
  TIMEOUT: 30000, // 30 seconds
});

export default {
  API_BASE_URL,
  PICOVOICE_ACCESS_KEY,
  TIMEOUT: 30000, // 30 seconds
};

