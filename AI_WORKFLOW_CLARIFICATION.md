# AI Workflow Clarification

## Overview

We use **three different AI models** for different purposes:

1. **Gemini Flash** → Instant conversational responses
2. **Gemini Pro** → Individual session analysis
3. **Cortex AI** → Long-term insights across multiple sessions

---

## Detailed Workflow

### 1. Instant Conversations (Gemini Flash)

**When**: User asks a question in real-time  
**Model**: Gemini Flash (fast, lightweight)  
**Endpoint**: `/api/ask`  
**Purpose**: Quick, conversational responses

```
User: "What is photosynthesis?"
    ↓
Gemini Flash generates quick answer
    ↓
ElevenLabs TTS converts to speech
    ↓
Response delivered instantly
```

**Use Case**: 
- Real-time voice conversations
- Quick Q&A
- Educational responses
- NOT for insights/analysis

---

### 2. Individual Session Analysis (Gemini Pro)

**When**: After each conversation session  
**Model**: Gemini Pro (detailed, comprehensive)  
**Endpoint**: `/api/analyze-session`  
**Purpose**: Analyze single conversation transcript

```
Audio uploaded
    ↓
ElevenLabs STT transcribes
    ↓
Gemini Pro analyzes transcript
    ↓
Generates development scores, strengths, activities
    ↓
Stored in Snowflake
```

**Output**:
- Development scores (language, cognitive, emotional, etc.)
- Strengths identified
- Growth opportunities
- Personalized activities
- Daily insight

**Use Case**:
- Per-session analysis
- Immediate feedback
- Detailed assessment of single conversation

---

### 3. Long-Term Insights (Cortex AI)

**When**: Viewing dashboard or requesting longitudinal analysis  
**Model**: Cortex AI (Snowflake native)  
**Endpoints**: `/api/cortex/analyze`, `/api/cortex/query`  
**Purpose**: Analyze aggregated data across multiple sessions

```
Multiple sessions in Snowflake
    ↓
Cortex analyzes aggregated data
    ↓
Generates long-term insights
    ↓
Displayed in dashboard
```

**Output**:
- Development trajectory (improving/stable/declining)
- Patterns across sessions
- Correlations between development areas
- Predictive insights
- Benchmark comparisons
- Natural language answers to questions

**Use Case**:
- Dashboard insights
- Long-term trends
- Pattern detection
- Predictive analytics
- Interactive chatbot

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│  REAL-TIME CONVERSATION                                 │
└─────────────────────────────────────────────────────────┘

User asks question
    ↓
┌─────────────────────────────────────────────────────────┐
│  Gemini Flash (Instant Response)                        │
│  - Fast, conversational                                 │
│  - Quick answers                                        │
│  - NOT for analysis                                     │
└─────────────────────────────────────────────────────────┘
    ↓
Response delivered


┌─────────────────────────────────────────────────────────┐
│  SESSION ANALYSIS                                       │
└─────────────────────────────────────────────────────────┘

Audio conversation ends
    ↓
ElevenLabs STT → Transcript
    ↓
┌─────────────────────────────────────────────────────────┐
│  Gemini Pro (Individual Session Analysis)               │
│  - Analyzes single transcript                           │
│  - Generates development scores                         │
│  - Identifies strengths & growth areas                 │
│  - Creates personalized activities                     │
└─────────────────────────────────────────────────────────┘
    ↓
Stored in Snowflake


┌─────────────────────────────────────────────────────────┐
│  LONG-TERM INSIGHTS                                     │
└─────────────────────────────────────────────────────────┘

User views dashboard
    ↓
Multiple sessions retrieved from Snowflake
    ↓
┌─────────────────────────────────────────────────────────┐
│  Cortex AI (Long-Term Analysis)                         │
│  - Analyzes aggregated data                             │
│  - Detects patterns & trends                            │
│  - Generates predictions                                │
│  - Compares to benchmarks                               │
│  - Answers natural language questions                   │
└─────────────────────────────────────────────────────────┘
    ↓
Insights displayed in dashboard
```

---

## Summary Table

| Purpose | Model | When | Output |
|---------|-------|------|--------|
| **Instant Responses** | Gemini Flash | Real-time Q&A | Quick conversational answers |
| **Session Analysis** | Gemini Pro | After each session | Development scores, strengths, activities |
| **Long-Term Insights** | Cortex AI | Dashboard viewing | Trends, patterns, predictions, chatbot |

---

## Key Points

### ✅ What Each Model Does

**Gemini Flash**:
- ✅ Instant conversational responses
- ✅ Quick Q&A
- ❌ NOT for analysis
- ❌ NOT for insights

**Gemini Pro**:
- ✅ Individual session analysis
- ✅ Detailed development assessment
- ✅ Per-conversation insights
- ❌ NOT for long-term trends

**Cortex AI**:
- ✅ Long-term trend analysis
- ✅ Pattern detection
- ✅ Predictive insights
- ✅ Interactive chatbot
- ✅ Benchmark comparisons
- ❌ NOT for instant responses
- ❌ NOT for individual session analysis

---

## For Hackathon

### What to Show Judges

1. **Real-Time Conversation** (Gemini Flash)
   - "Watch as the child asks a question"
   - "Gemini Flash provides instant response"
   - "ElevenLabs converts to natural speech"

2. **Session Analysis** (Gemini Pro)
   - "After conversation, Gemini Pro analyzes"
   - "Generates development scores"
   - "Stored in Snowflake"

3. **Long-Term Insights** (Cortex AI)
   - "Cortex AI analyzes 90 days of data"
   - "Shows trends and patterns"
   - "Interactive chatbot answers questions"

### Demo Script

**Opening**:
"Curiosity Companion uses a three-stage AI pipeline:
1. Gemini Flash for instant responses
2. Gemini Pro for individual session analysis
3. Cortex AI for long-term insights"

**Show**:
1. Real-time conversation (Gemini Flash)
2. Session analysis results (Gemini Pro)
3. Dashboard with Cortex insights
4. Chatbot asking questions (Cortex Analyst)

---

## API Endpoints

### Gemini Flash (Instant)
```
POST /api/ask
{
  "user_input": "What is photosynthesis?",
  "user_id": "user123"
}
```

### Gemini Pro (Session Analysis)
```
POST /api/analyze-session
{
  "audio_file": <file>,
  "child_age": 4,
  "child_name": "Tommy"
}
```

### Cortex AI (Long-Term Insights)
```
POST /api/cortex/analyze
{
  "child_id": "demo_child_tommy",
  "analysis_type": "trends",
  "days": 90
}

POST /api/cortex/query
{
  "child_id": "demo_child_tommy",
  "question": "What are the main trends?"
}
```

---

## Answer to Your Question

**"So we are using Gemini for instant and every other insight is through Cortex?"**

**Almost, but more nuanced:**

✅ **Gemini Flash** → Instant conversational responses (not insights)

✅ **Gemini Pro** → Individual session insights (per-conversation analysis)

✅ **Cortex AI** → Long-term insights (across multiple sessions)

**So the breakdown is:**
- **Instant responses** = Gemini Flash
- **Individual session insights** = Gemini Pro
- **Long-term insights** = Cortex AI

Both Gemini Pro and Cortex generate insights, but at different stages:
- Gemini Pro: Immediate, per-session insights
- Cortex: Long-term, aggregated insights

---

## Why This Architecture?

1. **Speed**: Gemini Flash for instant responses
2. **Depth**: Gemini Pro for detailed session analysis
3. **Scale**: Cortex AI for long-term pattern detection
4. **Integration**: Cortex runs in Snowflake (no external API calls)
5. **Cost**: Cortex included in Snowflake (vs. Gemini Pro API costs)

This gives you the best of all worlds! 🚀

