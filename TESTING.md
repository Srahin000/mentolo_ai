# 🧪 Testing Guide - HoloMentor Voice Pipeline

Quick guide to test your voice pipeline right now!

## ✅ What You Have (No Additional APIs Needed!)

You already have everything set up:
- ✅ Backend Flask server with `/api/ask` endpoint
- ✅ Groq Llama 3 70B integration
- ✅ ElevenLabs TTS integration
- ✅ React Native mobile app
- ✅ Modular API layer

**You don't need to add more APIs** - just test what's there!

---

## 🚀 Quick Test (3 Methods)

### Method 1: Python Test Script (Easiest!)

```bash
# Make sure backend is running first
cd backend
python app.py
# Keep this running in one terminal

# In another terminal, run test script
cd ..
python test_voice_pipeline.py
```

**What it tests:**
- ✅ Backend health check
- ✅ `/api/ask` endpoint
- ✅ Response format: `{text, audio_url, emotion}`
- ✅ Audio file accessibility

---

### Method 2: Browser Test (Visual!)

1. **Start backend:**
```bash
cd backend
python app.py
```

2. **Open browser and test:**
   - Go to: http://localhost:5000/api/health
   - Should see JSON with service status

3. **Test /api/ask with curl:**
```bash
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"user_input": "What is photosynthesis? Keep it brief."}'
```

4. **Copy the `audio_url` from response**
5. **Paste in browser** - audio should play!

---

### Method 3: Mobile App Test (Full Experience!)

1. **Start backend:**
```bash
cd backend
python app.py
```

2. **Update mobile config:**
```bash
cd mobile
# Edit config.js - add your computer's IP
nano config.js
```

3. **Start mobile app:**
```bash
npm install  # First time only
npm start
```

4. **Open in Expo Go:**
   - Scan QR code with Expo Go app
   - Press "Ask" button
   - See response + hear audio!

---

## 📋 Testing Checklist

### Backend Tests

- [ ] Backend starts without errors
- [ ] Health check shows all services ✓
- [ ] `/api/ask` returns `{text, audio_url, emotion}`
- [ ] Audio URL is accessible
- [ ] Audio file plays correctly

### Mobile App Tests

- [ ] Mobile app connects to backend
- [ ] "Ask" button triggers API call
- [ ] Response text appears in speech bubble
- [ ] Audio plays automatically
- [ ] Emotion badge shows correctly

---

## 🐛 Common Issues & Fixes

### "Backend not running"
```bash
cd backend
python app.py
# Should see: "Server starting on http://0.0.0.0:5000"
```

### "Service not available"
- Check `.env` file has correct API keys
- Verify keys at provider dashboards:
  - Groq: https://console.groq.com/
  - ElevenLabs: https://elevenlabs.io/
  - OpenAI: https://platform.openai.com/

### "Network request failed" (Mobile)
- Check `mobile/config.js` has correct IP
- Ensure phone and computer on same WiFi
- Verify backend is running

### "Audio not playing"
- Check audio URL in browser first
- Verify backend is serving files from `storage/audio/tts/`
- Check ElevenLabs API key is correct

---

## 🎯 Expected Results

### Successful Test Output:

```
🎤 HoloMentor Voice Pipeline Test
============================================================

🔍 Testing backend health...
✅ Backend is running!
   Service: HoloMentor Mobile AR

📊 Service Status:
   ✅ groq: Connected
   ✅ elevenlabs: Connected
   ✅ whisper: Connected

============================================================

🤖 Testing /api/ask endpoint...
📝 Sending question: 'What is photosynthesis? Keep it brief, one sentence.'

✅ Success! Response received:

📝 Text Response:
   Photosynthesis is the process by which plants convert sunlight, water, and carbon dioxide into glucose and oxygen...

🔊 Audio URL:
   http://localhost:5000/api/audio/tts/abc123.mp3

😊 Detected Emotion:
   curious

⚡ Response Time: 1.23s

🎵 Testing audio file access...
   ✅ Audio file is accessible!
   💡 You can play it at: http://localhost:5000/api/audio/tts/abc123.mp3

============================================================

✅ Voice Pipeline Test Complete!
```

---

## 🎓 What to Test Next

Once basic pipeline works:

1. **Different Questions:**
   - Try various topics
   - Test emotion detection
   - Check response quality

2. **Mobile App:**
   - Test on physical device
   - Verify audio playback
   - Check UI responsiveness

3. **Error Handling:**
   - Test with invalid input
   - Test with network issues
   - Test with missing API keys

---

## 💡 Pro Tips

- **Keep backend logs open** to see what's happening
- **Test audio URL in browser** before mobile app
- **Use test script first** to verify backend works
- **Check API quotas** if responses fail

---

**Ready to test?** Start with Method 1 (Python script) - it's the fastest! 🚀

