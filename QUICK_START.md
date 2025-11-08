# 🚀 HoloMentor Quick Start Guide

Get the full voice pipeline running in 5 minutes!

## Step 1: Backend (2 minutes)

```bash
# 1. Navigate to backend
cd backend

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Create .env file (in project root, not backend/)
cd ..
cp env.example .env

# 4. Add your API keys to .env
# Required: OPENAI_API_KEY, GROQ_API_KEY, ELEVENLABS_API_KEY
nano .env  # or use any text editor

# 5. Start backend server
cd backend
python app.py
```

**Expected output:**
```
🚀 Starting HoloMentor Mobile AR Backend
📡 Groq: ✓
🔊 ElevenLabs: ✓
🎤 Whisper: ✓
🌐 Server starting on http://0.0.0.0:5000
```

## Step 2: Mobile App (3 minutes)

```bash
# 1. Navigate to mobile
cd mobile

# 2. Install dependencies
npm install

# 3. Find your computer's IP address
# Mac/Linux:
ifconfig | grep "inet " | grep -v 127.0.0.1
# Windows:
ipconfig | findstr IPv4

# 4. Update config.js with your IP
nano config.js
# Change: const API_BASE_URL = 'http://YOUR_IP:5000/api';

# 5. Start Expo
npm start
```

**Expected output:**
```
› Metro waiting on exp://192.168.1.100:8081
› Scan the QR code above with Expo Go (Android) or the Camera app (iOS)
```

## Step 3: Test on Device

1. **Install Expo Go** on your phone (App Store / Play Store)
2. **Scan QR code** from terminal
3. **Press "Ask" button** in the app
4. **See response** appear in speech bubble
5. **Hear audio** play automatically

## ✅ Success Checklist

- [ ] Backend shows all services with ✓
- [ ] Mobile app connects to backend
- [ ] "Ask" button triggers API call
- [ ] Response text appears
- [ ] Audio plays successfully

## 🐛 Common Issues

**Backend won't start?**
- Check API keys in `.env` are correct
- Make sure port 5000 is free

**Mobile can't connect?**
- Verify IP address in `config.js`
- Ensure phone and computer on same WiFi
- Check backend is running

**No audio?**
- Check backend logs for TTS errors
- Verify ElevenLabs API key is correct

## 🎯 Next Steps

- Add speech-to-text input
- Integrate wake word detection
- Build Unity AR scene
- Add user profiles

---

**Need help?** Check the main README.md for detailed documentation!

