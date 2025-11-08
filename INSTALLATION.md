# 📦 Installation Guide - HoloMentor Mobile AR

Complete guide to install all requirements for the voice pipeline.

---

## 🐍 Python Requirements (Backend)

### Step 1: Check Python Version

```bash
python --version
# Should be Python 3.8 or higher

# Or try:
python3 --version
```

**If Python is not installed:**
- Mac: `brew install python3`
- Linux: `sudo apt-get install python3 python3-pip`
- Windows: Download from [python.org](https://www.python.org/downloads/)

### Step 2: Install Backend Dependencies

```bash
# Navigate to backend folder
cd backend

# Install all Python packages
pip install -r requirements.txt

# If you get permission errors, use:
pip install --user -r requirements.txt

# Or if using python3:
pip3 install -r requirements.txt
```

**This installs:**
- Flask (web server)
- Groq SDK (AI responses)
- ElevenLabs SDK (text-to-speech)
- OpenAI SDK (Whisper speech-to-text)
- Anthropic SDK (Claude - optional)
- Firebase Admin (optional)
- Audio processing libraries

### Step 3: Verify Installation

```bash
# Test if packages are installed
python -c "import flask; import groq; import elevenlabs; print('✅ All packages installed!')"
```

---

## 📱 Mobile App Requirements (React Native)

### Step 1: Install Node.js

```bash
node --version
# Should be Node 16 or higher

npm --version
```

**If Node.js is not installed:**
- Download from [nodejs.org](https://nodejs.org/)
- Or use: `brew install node` (Mac)

### Step 2: Install Expo CLI (Global)

```bash
npm install -g expo-cli
# or
npm install -g @expo/cli
```

### Step 3: Install Mobile Dependencies

```bash
# Navigate to mobile folder
cd mobile

# Install all npm packages
npm install

# This installs:
# - expo (React Native framework)
# - expo-av (audio playback)
# - expo-camera (camera access)
# - react-native (UI framework)
```

### Step 4: Verify Mobile Setup

```bash
# Check Expo is installed
npx expo --version

# Should show version number
```

---

## 🎯 Quick Installation (All at Once)

### For Backend:

```bash
cd backend
pip install -r requirements.txt
```

### For Mobile:

```bash
cd mobile
npm install
```

---

## 📋 Complete Requirements List

### Backend Python Packages:

```
flask==3.0.0              # Web server
flask-cors==4.0.0         # CORS support
python-dotenv==1.0.0      # Environment variables
groq==0.4.1               # Groq AI API
anthropic==0.8.1          # Claude API (optional)
elevenlabs==0.2.27        # ElevenLabs TTS
openai==4.20.1            # OpenAI Whisper
firebase-admin==6.3.0      # Firebase (optional)
soundfile==0.12.1         # Audio processing
librosa==0.10.1           # Audio analysis
pydub==0.25.1             # Audio manipulation
torch>=2.0.0              # ML framework
transformers>=4.30.0      # ML models
numpy>=1.24.0             # Numerical computing
scipy>=1.10.0             # Scientific computing
requests==2.31.0          # HTTP requests
gunicorn==21.2.0          # Production server
```

### Mobile npm Packages:

```
expo~49.0.0               # Expo framework
expo-av~13.4.1            # Audio playback
expo-camera~13.4.4        # Camera access
react 18.2.0              # React library
react-native 0.72.6       # React Native
react-native-safe-area-context 4.6.3
react-native-screens~3.22.0
```

---

## 🐛 Troubleshooting Installation

### Python Issues

**"pip: command not found"**
```bash
# Mac/Linux:
python3 -m pip install -r requirements.txt

# Or install pip:
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
```

**"Permission denied"**
```bash
pip install --user -r requirements.txt
```

**"Module not found" after installation**
```bash
# Make sure you're in the right directory
cd backend
pip install -r requirements.txt --upgrade
```

### Node.js Issues

**"npm: command not found"**
- Install Node.js from [nodejs.org](https://nodejs.org/)
- Or: `brew install node` (Mac)

**"expo: command not found"**
```bash
npm install -g @expo/cli
```

**"npm install fails"**
```bash
# Clear npm cache
npm cache clean --force

# Try again
npm install
```

### Large Downloads

**PyTorch is large (~2GB)**
- First install will take time
- This is normal - be patient!

**Expo downloads**
- First `npm install` downloads ~200MB
- This is normal

---

## ✅ Installation Checklist

### Backend:
- [ ] Python 3.8+ installed
- [ ] `pip install -r backend/requirements.txt` completed
- [ ] No error messages
- [ ] Can import packages: `python -c "import flask; import groq"`

### Mobile:
- [ ] Node.js 16+ installed
- [ ] Expo CLI installed globally
- [ ] `npm install` in mobile/ completed
- [ ] No error messages
- [ ] `npx expo --version` works

### Both:
- [ ] `.env` file created with API keys
- [ ] Ready to start backend: `cd backend && python app.py`
- [ ] Ready to start mobile: `cd mobile && npm start`

---

## 🚀 After Installation

1. **Start Backend:**
   ```bash
   cd backend
   python app.py
   ```

2. **Start Mobile (in another terminal):**
   ```bash
   cd mobile
   npm start
   ```

3. **Test:**
   ```bash
   python test_voice_pipeline.py
   ```

---

## 💡 Pro Tips

- **Use virtual environment** (optional but recommended):
  ```bash
  python3 -m venv venv
  source venv/bin/activate  # Mac/Linux
  # or: venv\Scripts\activate  # Windows
  pip install -r requirements.txt
  ```

- **Check disk space**: PyTorch needs ~2GB free space

- **Internet connection**: First install downloads large files

---

**Ready to install?** Start with backend requirements! 🚀

