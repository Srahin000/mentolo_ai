# 🔑 Where to Add Your API Keys

## 📍 Location: `.env` File in Project Root

The system looks for API keys in a file called **`.env`** in the project root directory.

**File path:** `/Users/sadmanrahin/Documents/Hackprinceton/.env`

---

## ✅ Step-by-Step

### 1. **Check if `.env` file exists**

```bash
cd /Users/sadmanrahin/Documents/Hackprinceton
ls -la | grep .env
```

You should see:
- `.env` (your actual keys - don't share this!)
- `env.example` (template file)

### 2. **If `.env` doesn't exist, create it:**

```bash
cp env.example .env
```

### 3. **Open `.env` file and add your keys:**

```bash
nano .env
# or
code .env
# or
open -e .env
```

### 4. **Add your API keys (replace the placeholders):**

```env
# REQUIRED - These 3 are needed for voice pipeline to work

OPENAI_API_KEY=sk-proj-paste-your-actual-key-here
GROQ_API_KEY=gsk_paste-your-actual-key-here
ELEVENLABS_API_KEY=paste-your-actual-key-here

# OPTIONAL - These are nice to have but not required

ANTHROPIC_API_KEY=sk-ant-paste-your-key-here
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# Server config
PORT=5000
DEBUG=True
```

### 5. **Save the file**

---

## 🔍 How the System Finds Your Keys

The backend code (`backend/app.py`) uses:

```python
from dotenv import load_dotenv
load_dotenv()  # This loads .env from project root
```

Then each service reads its key:

```python
# backend/services/groq_service.py
self.api_key = os.getenv('GROQ_API_KEY')  # Reads from .env

# backend/services/elevenlabs_service.py
self.api_key = os.getenv('ELEVENLABS_API_KEY')  # Reads from .env

# backend/services/whisper_service.py
self.api_key = os.getenv('OPENAI_API_KEY')  # Reads from .env
```

---

## ✅ Verify Keys Are Loaded

When you start the backend, you should see:

```bash
cd backend
python app.py
```

**Good output:**
```
🚀 Starting HoloMentor Mobile AR Backend
📡 Groq: ✓          ← Key found!
🔊 ElevenLabs: ✓    ← Key found!
🎤 Whisper: ✓       ← Key found!
```

**Bad output (keys missing):**
```
📡 Groq: ✗          ← Key NOT found!
🔊 ElevenLabs: ✗    ← Key NOT found!
🎤 Whisper: ✗       ← Key NOT found!
```

---

## 🎯 Quick Checklist

- [ ] `.env` file exists in project root (not in `backend/` folder)
- [ ] File contains `GROQ_API_KEY=...`
- [ ] File contains `ELEVENLABS_API_KEY=...`
- [ ] File contains `OPENAI_API_KEY=...`
- [ ] No quotes around the keys (unless key contains special chars)
- [ ] No spaces around the `=` sign
- [ ] Backend shows ✓ for all services when started

---

## 🐛 Common Mistakes

### ❌ Wrong location:
```
backend/.env  ← WRONG! (too deep)
.env          ← CORRECT! (project root)
```

### ❌ Wrong format:
```env
GROQ_API_KEY = gsk_abc123  ← WRONG (spaces around =)
GROQ_API_KEY=gsk_abc123    ← CORRECT
```

### ❌ Quotes when not needed:
```env
GROQ_API_KEY="gsk_abc123"  ← Usually not needed
GROQ_API_KEY=gsk_abc123    ← Usually correct
```

### ❌ Typo in variable name:
```env
GROQ_API_KEY=gsk_abc123     ← CORRECT
GROQ_API_KEYS=gsk_abc123    ← WRONG (extra 'S')
```

---

## 📝 Example `.env` File

```env
# Required for voice pipeline
OPENAI_API_KEY=sk-proj-abc123xyz789def456
GROQ_API_KEY=gsk_def456uvw012ghi789
ELEVENLABS_API_KEY=abc123def456ghi789jkl012

# Optional
ANTHROPIC_API_KEY=sk-ant-mno345pqr678stu901
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# Server config
PORT=5000
DEBUG=True
HOST=0.0.0.0
```

---

## 🔒 Security Note

**NEVER commit `.env` to Git!**

The `.gitignore` file should already block it, but double-check:
```bash
git status
# Should NOT show .env in the list
```

---

## 💡 Still Not Working?

1. **Check file location:**
   ```bash
   pwd  # Should be in project root
   ls -la .env  # Should exist
   ```

2. **Check file contents:**
   ```bash
   cat .env | grep -E "GROQ|ELEVENLABS|OPENAI"
   # Should show your keys
   ```

3. **Restart backend** after adding keys:
   ```bash
   # Stop backend (Ctrl+C)
   # Start again
   python backend/app.py
   ```

4. **Check backend logs** for error messages

---

**Your keys go in `.env` file in the project root!** 🎯

