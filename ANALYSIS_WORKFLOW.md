# Child Development Analysis Workflow

## Two-Stage Analysis Process

Our system uses a **two-stage analysis approach** for comprehensive child development insights:

### Stage 1: Individual Session Analysis (Gemini Pro)
**When**: Each time a conversation session is analyzed  
**Who**: Gemini Pro (Google's advanced AI model)  
**What**: Analyzes individual conversation transcripts for immediate insights

### Stage 2: Long-Term Analysis (Cortex)
**When**: When viewing child profile or requesting longitudinal insights  
**Who**: Snowflake Cortex (AI-powered SQL analysis)  
**What**: Analyzes aggregated data across multiple sessions for long-term trends

---

## Detailed Workflow

### 1. Session Upload & Analysis

```
Parent uploads audio → ElevenLabs STT → Transcript
                                    ↓
                    Gemini Pro analyzes transcript
                                    ↓
                    Stores analysis in Snowflake
```

**Endpoint**: `POST /api/analyze-session`

**Process**:
1. Audio file uploaded
2. ElevenLabs transcribes audio to text
3. **Gemini Pro analyzes the transcript**:
   - Language development indicators
   - Cognitive patterns
   - Emotional intelligence markers
   - Social skills
   - Creativity indicators
   - Speech clarity
   - Generates scores (0-100) for each area
4. Analysis stored in Snowflake `child_development_sessions` table

**Gemini Pro Output**:
```json
{
  "daily_insight": "Tommy used 8 new words today...",
  "development_snapshot": {
    "language": {"level": "growing", "score": 75},
    "cognitive": {"level": "strong", "score": 82},
    ...
  },
  "strengths": [...],
  "growth_opportunities": [...],
  "personalized_activities": [...]
}
```

### 2. Long-Term Analysis (Cortex)

```
Multiple sessions in Snowflake → Cortex analyzes aggregated data
                                            ↓
                    Long-term insights, trends, predictions
```

**Endpoint**: `GET /api/child-profile/<child_id>`

**Process**:
1. Retrieves all sessions from Snowflake (already analyzed by Gemini Pro)
2. **Cortex analyzes the aggregated data**:
   - Overall development trajectory
   - Patterns across sessions
   - Correlations between development areas
   - Predictive insights
   - Benchmark comparisons
3. Returns both:
   - Individual session data (from Gemini Pro)
   - Long-term insights (from Cortex)

**Cortex Output**:
```json
{
  "cortex_insights": {
    "trajectory": "improving",
    "strengths": [
      {
        "area": "Language Development",
        "evidence": "Vocabulary growth rate of 15 words/week",
        "why_matters": "Indicates strong language acquisition"
      }
    ],
    "growth_areas": [...],
    "predictions": [...],
    "recommendations": [...]
  }
}
```

---

## Why Two Stages?

### Gemini Pro (Stage 1)
✅ **Best for**: Individual session analysis  
✅ **Strengths**:
- Deep understanding of conversation context
- Holistic analysis of single interactions
- Generates detailed, actionable insights per session
- Works globally (no region restrictions)

### Cortex (Stage 2)
✅ **Best for**: Long-term trend analysis  
✅ **Strengths**:
- Analyzes data directly in Snowflake (no data export)
- SQL-powered aggregation across many sessions
- Pattern detection across time
- Privacy-preserving (data stays in Snowflake)
- Cost-effective (included in Snowflake)

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    SESSION ANALYSIS                          │
└─────────────────────────────────────────────────────────────┘

Audio File
    ↓
ElevenLabs STT
    ↓
Transcript
    ↓
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1: Gemini Pro Analysis                               │
│  - Analyzes individual transcript                            │
│  - Generates development scores                               │
│  - Identifies strengths & growth areas                       │
│  - Creates personalized activities                           │
└─────────────────────────────────────────────────────────────┘
    ↓
Stored in Snowflake
(child_development_sessions table)

┌─────────────────────────────────────────────────────────────┐
│              LONG-TERM ANALYSIS                              │
└─────────────────────────────────────────────────────────────┘

Multiple Sessions (90 days)
    ↓
┌─────────────────────────────────────────────────────────────┐
│  STAGE 2: Cortex Analysis                                    │
│  - Analyzes aggregated data                                  │
│  - Detects patterns & trends                                 │
│  - Generates predictions                                     │
│  - Compares to benchmarks                                    │
└─────────────────────────────────────────────────────────────┘
    ↓
Long-term Insights
    ↓
Dashboard / API Response
```

---

## API Endpoints

### Stage 1: Individual Session Analysis

**POST `/api/analyze-session`**
- Input: Audio file, child_age, child_name
- Process: Gemini Pro analyzes transcript
- Output: Detailed session analysis
- Storage: Saved to Snowflake

### Stage 2: Long-Term Analysis

**GET `/api/child-profile/<child_id>`**
- Input: Child ID
- Process: 
  1. Retrieves all sessions (Gemini Pro analyzed)
  2. Cortex analyzes aggregated data
- Output: Individual sessions + long-term insights

**POST `/api/cortex/analyze`**
- Input: Child ID, analysis type, days
- Process: Cortex analyzes stored sessions
- Output: Long-term insights only

---

## Example Usage

### 1. Analyze a Session (Gemini Pro)

```bash
curl -X POST http://localhost:5000/api/analyze-session \
  -F "audio_file=@conversation.mp3" \
  -F "child_age=4" \
  -F "child_name=Tommy" \
  -F 'session_context={"duration_minutes": 3}'
```

**Response** (Gemini Pro analysis):
```json
{
  "session_id": "abc123",
  "analysis": {
    "daily_insight": "Tommy used 8 new words today...",
    "development_snapshot": {
      "language": {"score": 75},
      "cognitive": {"score": 82}
    }
  }
}
```

### 2. Get Long-Term Insights (Cortex)

```bash
curl http://localhost:5000/api/child-profile/demo_child_tommy
```

**Response** (Gemini Pro + Cortex):
```json
{
  "sessions": [
    {
      "analysis": { /* Gemini Pro analysis */ }
    }
  ],
  "trends": {
    "vocabulary_growth": [...],
    "cortex_insights": {
      "trajectory": "improving",
      "strengths": [...],
      "predictions": [...]
    },
    "analysis_source": "cortex"
  }
}
```

---

## Fallback Behavior

### If Cortex Unavailable

If Cortex is not available in your region:
- ✅ Gemini Pro still analyzes individual sessions
- ✅ Standard SQL trends still work
- ✅ Dashboard displays Gemini Pro insights
- ⚠️ Long-term Cortex insights not available
- ✅ System gracefully degrades

**Response**:
```json
{
  "trends": {
    "vocabulary_growth": [...],
    "analysis_source": "gemini_pro"  // No Cortex insights
  }
}
```

---

## Summary

| Stage | AI Model | Purpose | When |
|-------|----------|---------|------|
| **1** | Gemini Pro | Individual session analysis | Each session upload |
| **2** | Cortex | Long-term trend analysis | Viewing child profile |

**Key Points**:
- ✅ Gemini Pro analyzes each session first
- ✅ Cortex analyzes aggregated data second
- ✅ Both insights available in dashboard
- ✅ Graceful fallback if Cortex unavailable

This two-stage approach ensures you get both immediate insights (Gemini Pro) and long-term patterns (Cortex) for comprehensive child development tracking.

