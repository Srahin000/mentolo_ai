# 🔑 API Keys Setup Guide

## Required API Keys (Get All 3!)

### 1. **OpenAI API Key** (Whisper Speech-to-Text)
**Get it here:** https://platform.openai.com/api-keys

**Steps:**
1. Sign up/login to OpenAI
2. Go to API Keys section
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

**Free Tier:** $5 free credit (enough for ~300 minutes of audio)

**Add to .env:**
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

---

### 2. **Groq API Key** (Fast AI Responses)
**Get it here:** https://console.groq.com/keys

**Steps:**
1. Sign up at console.groq.com
2. Navigate to API Keys
3. Create new key
4. Copy it (starts with `gsk_`)

**Free Tier:** 30 requests/minute (plenty for hackathon!)

**Add to .env:**
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
```

---

### 3. **ElevenLabs API Key** (Text-to-Speech)
**Get it here:** https://elevenlabs.io/

**Steps:**
1. Sign up at elevenlabs.io
2. Go to Profile → API Keys
3. Generate API key
4. Copy it

**Free Tier:** 10,000 characters/month (great for demos!)

**Add to .env:**
```
ELEVENLABS_API_KEY=xxxxxxxxxxxxx
```

---

## Optional Keys (For Enhanced Features)

### 4. **Anthropic Claude API Key** (Lesson Plans)
**Get it here:** https://console.anthropic.com/

**Steps:**
1. Sign up at Anthropic
2. Go to API Keys
3. Create key (starts with `sk-ant-`)

**Free Tier:** Limited free credits

**Add to .env:**
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

---

### 5. **Firebase** (User Progress Tracking)
**Get it here:** https://console.firebase.google.com/

**Steps:**
1. Create new Firebase project
2. Go to Project Settings → Service Accounts
3. Generate new private key
4. Download JSON file
5. Save as `firebase-credentials.json` in project root

**Add to .env:**
```
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
```

---

## Quick Setup

1. **Copy the template:**
```bash
cp env.example .env
```

2. **Edit .env file:**
```bash
nano .env
# or
code .env
```

3. **Paste your keys:**
```env
# Required
OPENAI_API_KEY=sk-proj-your-key-here
GROQ_API_KEY=gsk_your-key-here
ELEVENLABS_API_KEY=your-key-here

# Optional
ANTHROPIC_API_KEY=sk-ant-your-key-here
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# Config
PORT=5000
DEBUG=True
```

4. **Test it works:**
```bash
python app.py
# Should see: ✓ marks next to each service
```

---

## Cost Breakdown (Free Tiers)

| Service | Free Tier | Enough For |
|---------|-----------|------------|
| **OpenAI Whisper** | $5 credit | ~300 min audio |
| **Groq** | 30 req/min | Unlimited for hackathon |
| **ElevenLabs** | 10K chars/month | ~50 responses |
| **Claude** (optional) | Limited credits | 10-20 lesson plans |
| **Firebase** (optional) | Free Spark plan | 1GB storage |

**Total Cost for Hackathon:** $0 (all free tiers!) 🎉

---

## Security Note

⚠️ **NEVER commit .env to GitHub!**

The `.gitignore` file already blocks it, but double-check:
```bash
# Make sure .env is not tracked
git status
# Should NOT show .env
```

---

## Troubleshooting

### "Service not available" error
- Check your API key is correct
- Verify you have credits/quota remaining
- Test the key at the provider's dashboard

### Keys not loading
- Make sure `.env` file is in project root (same folder as `app.py`)
- Check for typos in variable names
- Restart the server after adding keys

### Rate limits
- Groq: Wait a minute between bursts
- OpenAI: Check usage dashboard
- ElevenLabs: Monitor character count

---

**Ready to go?** Run `python app.py` and start building! 🚀

