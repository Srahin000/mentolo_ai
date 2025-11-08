# HoloMentor Mobile - React Native App

React Native mobile app with Expo for fast iteration. This will later integrate Unity AR.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ installed
- Expo CLI: `npm install -g expo-cli`
- iOS Simulator (Mac) or Android Emulator, or Expo Go app on physical device

### Installation

```bash
cd mobile
npm install
```

### Configuration

1. **Update API URL** in `config.js`:
   - For local development: Use your computer's IP address
   - Find your IP: 
     - Mac/Linux: `ifconfig | grep "inet " | grep -v 127.0.0.1`
     - Windows: `ipconfig | findstr IPv4`
   - Example: `const API_BASE_URL = 'http://192.168.1.100:5000/api';`

2. **Make sure backend is running**:
   ```bash
   cd ../backend
   python app.py
   ```

### Run the App

```bash
# Start Expo
npm start

# Or run on specific platform
npm run ios      # iOS Simulator
npm run android  # Android Emulator
```

### Testing on Physical Device

1. Install **Expo Go** app on your phone
2. Make sure phone and computer are on same WiFi network
3. Scan QR code from terminal
4. App will load on your device

## 📱 Features

- **Camera View**: AR placeholder with live camera feed
- **Ask Button**: Floating button to trigger AI questions
- **Speech Bubble**: Displays AI response text
- **Audio Playback**: Plays ElevenLabs TTS audio responses
- **Emotion Display**: Shows detected emotion from user input

## 🔧 Architecture

### Modular API Layer (`api.js`)
- `askQuestion()` - Calls `/api/ask` endpoint
- `playAudio()` - Placeholder for audio playback
- `checkHealth()` - Backend health check
- `generatePlan()` - Lesson plan generation

**This API layer can be reused by Unity later!**

### ARPlaceholder Screen
- Camera view (will be replaced with Unity AR)
- UI overlay with Ask button
- Speech bubble for responses
- Audio playback integration

## 🔄 Future Unity Integration

When Unity AR is ready:
1. Replace `ARPlaceholder.js` with Unity view
2. Use same `api.js` functions (or port to C#)
3. Unity will call same `/api/ask` endpoint
4. Audio playback in Unity using AudioSource

## 📝 Notes

- Currently uses test question "What is photosynthesis?"
- Later: Add speech-to-text input
- Later: Add text input field as alternative
- Later: Wake word detection integration

## 🐛 Troubleshooting

**"Network request failed"**
- Check `config.js` has correct IP address
- Make sure backend is running
- Ensure phone and computer on same WiFi

**"Camera permission denied"**
- Grant permission when prompted
- Check device settings

**Audio not playing**
- Check audio URL is accessible
- Verify backend is serving audio files correctly

