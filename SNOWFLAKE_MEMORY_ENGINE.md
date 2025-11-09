# Snowflake Memory Engine - Complete Guide
## "Gemini teaches. Snowflake learns."

---

## 🧠 Core Concept

**"Snowflake is the Brain Between Sessions"**

Every interaction is:
1. **Stored** with vector embeddings
2. **Retrieved** via RAG for personalization
3. **Analyzed** by Cortex for insights
4. **Learned** from to improve teaching

---

## 🎯 What We Built

### 1. **Vector Embeddings (Memory Storage)**

Every interaction is embedded using `CORTEX.EMBED_TEXT`:

```sql
SELECT SNOWFLAKE.CORTEX.EMBED_TEXT('snowflake-arctic', question_text) AS embedding
FROM user_embeddings
```

**Stores**:
- Question text
- Answer text
- Emotion
- Topic
- Lesson tag
- Confidence score
- Vector embedding (1024 dimensions)

### 2. **RAG Pipeline (Retrieval-Augmented Generation)**

When user asks a question:
1. Generate embedding for current question
2. Find similar past interactions (vector similarity)
3. Retrieve top 3-5 relevant memories
4. Pass to Gemini for personalized response

```sql
SELECT * FROM user_embeddings
ORDER BY VECTOR_DISTANCE(embedding, :current_question)
LIMIT 3
```

**Result**: "Previously, you struggled with Newton's 2nd Law — shall we review that?"

### 3. **Cortex COMPLETE for Insights**

**Learning Summary**:
```sql
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'snowflake-arctic',
    'Summarize this learner's progress: ' || ALL_RESPONSES
) AS progress_summary
```

**Cohort Analytics**:
```sql
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'snowflake-arctic',
    'Analyze which tone correlates with higher retention scores'
) AS analysis
```

### 4. **Knowledge Gap Tracking**

Tracks recurring struggles:
- Topic
- Concept
- Frequency
- Context
- Resolution status

---

## 📊 API Endpoints

### Memory Endpoints

**GET `/api/memory/context`**
- Retrieve relevant past interactions (RAG)
- Query params: `user_id`, `question`
- Returns: Context string + memories array

**GET `/api/memory/summary`**
- Generate learning summary using Cortex COMPLETE
- Query params: `user_id`, `days`
- Returns: AI-generated summary + knowledge gaps

**GET `/api/memory/cohort-insights`**
- Analyze patterns across all users
- Query params: `topic` (optional)
- Returns: Cohort analysis + recommendations

**POST `/api/memory/knowledge-gap`**
- Track a knowledge gap
- Body: `user_id`, `topic`, `concept`, `context`
- Returns: Success status

---

## 🔄 Complete Workflow

```
┌─────────────────────────────────────────────────────────┐
│  REAL-TIME: Gemini Teaches                              │
└─────────────────────────────────────────────────────────┘

User asks question
    ↓
Snowflake Memory retrieves similar past interactions (RAG)
    ↓
Gemini uses context: "Previously, you asked about..."
    ↓
Gemini responds with personalized answer
    ↓
┌─────────────────────────────────────────────────────────┐
│  STORAGE: Snowflake Learns                               │
└─────────────────────────────────────────────────────────┘

Interaction stored with vector embedding
    ↓
Cortex EMBED_TEXT generates embedding
    ↓
Stored in user_embeddings table
    ↓
┌─────────────────────────────────────────────────────────┐
│  ANALYSIS: Cortex Thinks                                 │
└─────────────────────────────────────────────────────────┘

Cortex COMPLETE analyzes:
- Learning summaries
- Cohort patterns
- Teaching effectiveness
- Knowledge gaps
    ↓
Insights displayed in dashboard
```

---

## 🏆 Hackathon Showcase Features

### ✅ Vector Embeddings
- **CORTEX.EMBED_TEXT** for every interaction
- Creates personalized memory
- Enables RAG pipeline

### ✅ RAG Pipeline
- Vector similarity search
- Context retrieval
- Personalization

### ✅ Cortex COMPLETE
- Learning summaries
- Cohort analytics
- Teaching effectiveness analysis

### ✅ Knowledge Gap Tracking
- Identifies recurring struggles
- Tracks frequency
- Suggests remediation

### ✅ Self-Improving System
- Learns from every interaction
- Identifies what works
- Adapts teaching approach

---

## 📝 SQL Queries for Dashboard

See `snowflake_memory_queries.sql` for:
- Memory engine status
- Most discussed topics
- Knowledge gaps tracking
- Learning summaries (Cortex)
- Cohort analytics (Cortex)
- Vector similarity examples
- Memory growth over time
- Teaching effectiveness analysis

---

## 🎯 Narrative for Judges

**"Gemini teaches. Snowflake learns."**

1. **Real-time**: Gemini Flash provides instant responses
2. **Memory**: Snowflake stores every interaction with embeddings
3. **Personalization**: RAG retrieves relevant past conversations
4. **Insights**: Cortex AI analyzes patterns and generates summaries
5. **Learning**: System improves by identifying what works

**"Snowflake is the Brain Between Sessions"**

---

## ✅ Integration Checklist

- [x] Vector embeddings (CORTEX.EMBED_TEXT)
- [x] RAG pipeline (vector similarity search)
- [x] Memory storage (user_embeddings table)
- [x] Knowledge gap tracking
- [x] Cortex COMPLETE for summaries
- [x] Cohort analytics
- [x] API endpoints
- [x] Dashboard integration
- [x] Clear narrative

---

## 🚀 Ready to Win!

This architecture showcases:
- ✅ **Snowflake Cortex AI** (embeddings, COMPLETE)
- ✅ **RAG Pipeline** (vector search, personalization)
- ✅ **Self-Improving** (learns from data)
- ✅ **Complete Story** ("Gemini teaches. Snowflake learns.")

**Perfect for Snowflake sponsor track!** 🏆

