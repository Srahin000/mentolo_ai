# 🎤 HoloMentor Mobile AR - Full-Stack AI Voice Assistant

**Modular AI-powered voice assistant for mobile with future Unity AR integration**

> **Voice Pipeline:** User Input → Gemini AI → ElevenLabs TTS → Mobile Playback  
> **Analytics:** Every interaction logged to Snowflake for personalized AI insights

---

## 🏗️ Project Structure

```
HoloMentor/
├── backend/              # Flask API server
│   ├── app.py           # Main Flask app with /api/ask endpoint
│   ├── services/        # AI service integrations
│   ├── storage/         # Audio files and sessions
│   └── requirements.txt
│
├── mobile/              # React Native app (Expo)
│   ├── App.js           # Main entry point
│   ├── ARPlaceholder.js # Camera view with Ask button
│   ├── api.js           # Modular API functions (reusable for Unity)
│   ├── config.js        # API configuration
│   └── package.json
│
└── .env                 # API keys (create this!)
```

---

## 🚀 Quick Start

### 1. **Backend Setup**

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file in project root (not backend/)
cp ../env.example ../.env
# Edit ../.env with your API keys

# Start Flask server
python app.py
```

Server runs at: **http://localhost:5000**

### 2. **Mobile App Setup**

```bash
# Navigate to mobile
cd mobile

# Install dependencies
npm install

# Update API URL in config.js
# Replace YOUR_IP_ADDRESS with your computer's IP
# Find IP: ifconfig | grep "inet " | grep -v 127.0.0.1

# Start Expo
npm start
```

### 3. **Test the Pipeline**

1. Backend running on port 5000
2. Mobile app connected to backend
3. Press "Ask" button in app
4. See AI response text + hear audio playback

---

## 📡 API Endpoints

### **`POST /api/ask`** - Core Voice Assistant

**Request:**
```json
{
  "user_input": "What is photosynthesis?",
  "user_id": "optional",
  "context": {}
}
```

**Response:**
```json
{
  "text": "Photosynthesis is how plants make food...",
  "audio_url": "http://localhost:5000/api/audio/tts/abc123.mp3",
  "emotion": "curious"
}
```

### **`GET /api/health`** - Health Check

Returns service status and availability.

### **`GET /api/dashboard`** - Dashboard with AI Insights

Get comprehensive dashboard data with personalized insights.

**Headers:**
- `X-User-ID`: User identifier (required)

**Response:**
```json
{
  "summary": {
    "total_interactions": 45,
    "active_days": 12,
    "engagement_score": 0.75,
    "most_common_emotion": "excited"
  },
  "ai_insights": [
    "🌟 Great progress! You've had 45 learning interactions.",
    "⚡ Fast responses show you're asking great questions!"
  ],
  "recommendations": [...]
}
```

### **`GET/POST/PUT /api/user/profile`** - User Profile Management

Get, create, or update user profile with learning goals and preferences.

### **`GET /api/analytics/insights`** - AI-Powered Insights

Get personalized insights based on learning patterns.

**See `DASHBOARD_API.md` for full API documentation.**

---

## 🎯 Current Features (Phase 1)

✅ **Backend:**
- Flask server with CORS enabled
- `/api/ask` endpoint: Gemini → ElevenLabs pipeline
- Returns `{text, audio_url, emotion}`
- Audio file serving
- **User data storage** with automatic interaction logging
- **Snowflake analytics** for AI-powered insights
- **Dashboard API** with personalized recommendations

✅ **Mobile App:**
- React Native with Expo
- Camera view (AR placeholder)
- Floating "Ask" button
- Speech bubble overlay
- Audio playback with expo-av
- Modular `api.js` for future Unity reuse

---

## 🔄 Future Unity Integration (Phase 2)

The architecture is designed for seamless Unity integration:

1. **Same API Endpoints**: Unity will call same `/api/ask`
2. **Reusable Logic**: `api.js` functions can be ported to C# Unity scripts
3. **Audio Playback**: Unity AudioSource will play same MP3 files
4. **AR Scene**: Replace React Native camera view with Unity AR Foundation

**Unity Integration Plan:**
- Use `UnityWebRequest` to call `/api/ask`
- Play audio with `AudioSource.PlayOneShot()`
- Trigger avatar animations based on `emotion` field
- Use AR Foundation for holographic mentor

---

## 🔧 Configuration

### Backend (`backend/app.py`)
- Port: 5000 (configurable via `PORT` env var)
- Host: `0.0.0.0` (allows mobile connections)
- CORS: Enabled for all origins

### Mobile (`mobile/config.js`)
```javascript
const API_BASE_URL = 'http://YOUR_IP:5000/api';
```

**Find your IP:**
- Mac/Linux: `ifconfig | grep "inet " | grep -v 127.0.0.1`
- Windows: `ipconfig | findstr IPv4`

---

## 📱 Mobile App Usage

1. **Start Backend**: `cd backend && python app.py`
2. **Start Mobile**: `cd mobile && npm start`
3. **Open in Expo Go**: Scan QR code with Expo Go app
4. **Press "Ask" Button**: Triggers test question
5. **See Response**: Text appears in speech bubble
6. **Hear Audio**: ElevenLabs TTS plays automatically

**Current Test Question**: "What is photosynthesis? Keep it brief."

---

## 🎨 Modular Architecture

### **API Layer (`mobile/api.js`)**

Functions designed for reuse:

```javascript
// React Native
import { askQuestion } from './api';
const response = await askQuestion("What is photosynthesis?");

// Future Unity (C# equivalent)
var response = await API.AskQuestion("What is photosynthesis?");
```

**Functions:**
- `askQuestion(userInput, userId, context)` - Main AI query
- `playAudio(audioUrl)` - Audio playback (platform-specific)
- `checkHealth()` - Backend health check
- `generatePlan(topic, planType, userId, parameters)` - Lesson plans

---

## 🔑 API Keys Required

See `API_KEYS.md` for detailed setup:

1. **OpenAI** (Whisper) - https://platform.openai.com/api-keys
2. **Groq** (Llama 3 70B) - https://console.groq.com/keys
3. **ElevenLabs** (TTS) - https://elevenlabs.io/

Optional:
4. **Anthropic** (Claude) - https://console.anthropic.com/
5. **Firebase** - https://console.firebase.google.com/
6. **Snowflake** (Analytics & AI Insights) - https://app.snowflake.com/

---

## 🐛 Troubleshooting

### Backend Issues

**"Service not available"**
- Check API keys in `.env` file
- Verify keys are correct and have credits

**"Port already in use"**
- Change `PORT=5001` in `.env`
- Update mobile `config.js` accordingly

### Mobile Issues

**"Network request failed"**
- Check `config.js` has correct IP address
- Ensure phone and computer on same WiFi
- Verify backend is running

**"Camera permission denied"**
- Grant permission when prompted
- Check device settings

**Audio not playing**
- Check audio URL is accessible
- Verify backend is serving files

---

## 📚 Documentation

- **Backend API**: See `backend/app.py` for endpoint details
- **Mobile App**: See `mobile/README.md` for React Native setup
- **API Keys**: See `API_KEYS.md` for key setup instructions
- **Dashboard & Analytics**: See `DASHBOARD_API.md` for Snowflake integration and insights

---

## 🎓 Hackathon Tips

### Demo Flow:
1. Show backend health check (all services ✓)
2. Press "Ask" in mobile app
3. Show AI response appearing
4. Play audio response
5. Explain modular architecture for Unity integration

### Key Points:
- **Speed**: Groq responses in ~1 second
- **Voice Quality**: Natural ElevenLabs TTS
- **Modular**: Same API for React Native and Unity
- **Future-Ready**: AR integration ready

---

## 📄 License

MIT License - Free to use and modify!

---

**Ready to build?** Start with the backend, then mobile app! 🚀
