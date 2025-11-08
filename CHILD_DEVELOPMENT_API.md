# Child Development Dashboard API

Complete API documentation for the child development analysis system.

## Overview

The system analyzes voice conversations between parents and children to provide comprehensive development insights, personalized activities, and longitudinal tracking.

**Pipeline:** Audio → ElevenLabs STT → Gemini Analysis → Firebase/Snowflake Storage → Dashboard Insights

---

## Endpoints

### 1. Analyze Session
**`POST /api/analyze-session`**

Analyze a voice conversation session for child development insights.

**Request (multipart/form-data):**
```
audio_file: <file> (MP3, WAV, etc.)
child_age: 4 (integer, required)
child_name: "Tommy" (string, required)
session_context: '{"duration_minutes": 3, "known_interests": ["trucks", "dinosaurs"]}' (JSON string, optional)
X-User-ID: user123 (header, optional)
```

**Response:**
```json
{
  "session_id": "abc-123-def",
  "transcript": "Parent: What did you do today? Child: I played with trucks...",
  "analysis": {
    "daily_insight": "Tommy used 8 new words today, including 'magnificent' and 'investigate'!",
    "development_snapshot": {
      "language": {"level": "strong", "score": 85},
      "cognitive": {"level": "growing", "score": 78},
      "emotional": {"level": "growing", "score": 72},
      "social": {"level": "strong", "score": 80},
      "creativity": {"level": "growing", "score": 75}
    },
    "strengths": [
      {
        "title": "Storytelling Genius",
        "evidence": "Tommy creates stories with clear beginnings, middles, and ends",
        "why_matters": "Strong narrative skills support reading comprehension"
      }
    ],
    "growth_opportunities": [
      {
        "area": "Emotional Vocabulary",
        "current": "Uses basic emotion words",
        "next_step": "Introduce nuanced emotions like 'frustrated' or 'proud'"
      }
    ],
    "personalized_activities": [
      {
        "title": "Truck Story Adventure",
        "duration": "15 minutes",
        "materials": ["toy trucks", "paper", "crayons"],
        "instructions": "Have Tommy create a story about trucks...",
        "impact_areas": ["language", "creativity"],
        "based_on_interests": ["trucks", "storytelling"]
      }
    ],
    "vocabulary_analysis": {
      "new_words_used": ["magnificent", "investigate"],
      "vocabulary_size_estimate": 850,
      "sentence_complexity": 7.2,
      "question_frequency": 12
    },
    "milestone_progress": {
      "on_track": ["Uses 4-5 word sentences", "Tells stories with details"],
      "emerging": ["Asks 'why' questions"],
      "ahead": ["Uses complex vocabulary"]
    },
    "parent_encouragement": "Tommy is showing excellent language development! Keep encouraging his curiosity."
  },
  "timestamp": "2025-11-08T12:34:56Z"
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:5000/api/analyze-session \
  -H "X-User-ID: parent-123" \
  -F "audio_file=@conversation.mp3" \
  -F "child_age=4" \
  -F "child_name=Tommy" \
  -F 'session_context={"duration_minutes": 3, "known_interests": ["trucks"]}'
```

---

### 2. Get Child Profile
**`GET /api/child-profile/<child_id>`**

Get aggregated child profile with longitudinal analysis and trends.

**Response:**
```json
{
  "child_id": "parent-123",
  "profile": {
    "child_name": "Tommy",
    "child_age": 4,
    "total_sessions": 15,
    "last_session": "2025-11-08T12:34:56Z"
  },
  "sessions": [
    {
      "session_id": "abc-123",
      "timestamp": "2025-11-08T12:34:56Z",
      "analysis": { ... }
    }
  ],
  "trends": {
    "vocabulary_growth": [800, 820, 850, 870],
    "complexity_progression": [6.5, 6.8, 7.0, 7.2],
    "consistency": 0.5,
    "timeline": [
      {
        "date": "2025-11-01",
        "vocabulary_size": 800,
        "sentence_complexity": 6.5,
        "language": 80,
        "cognitive": 75
      }
    ],
    "trend_direction": "improving"
  },
  "total_sessions": 15
}
```

**Example:**
```bash
curl http://localhost:5000/api/child-profile/parent-123
```

---

### 3. Adaptive Learning
**`GET /api/adaptive-learning/<child_id>`**

Get personalized activities based on child's interests and learning style.

**Response:**
```json
{
  "interests": ["trucks", "dinosaurs", "building"],
  "known_concepts": ["colors", "counting", "shapes"],
  "learning_style": "kinesthetic",
  "personalized_activities": [
    {
      "title": "Color Sorting with Trucks",
      "description": "Sort toy trucks by color while practicing counting",
      "materials": ["toy trucks", "colored bins"],
      "instructions": "1. Set up colored bins...",
      "learning_goals": ["color recognition", "counting", "sorting"],
      "age_appropriate": true
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:5000/api/adaptive-learning/parent-123
```

---

## Data Storage

### Firebase Collections

1. **`child_sessions`** - Full session data with analysis
   - Document ID: `session_id`
   - Fields: `session_id`, `user_id`, `child_name`, `child_age`, `transcript`, `analysis`, `timestamp`

2. **`child_profiles`** - Child profile summaries
   - Document ID: `user_id`
   - Fields: `child_name`, `child_age`, `total_sessions`, `last_session`

### Snowflake Tables

1. **`child_development_sessions`** - Detailed session data
   - Stores full analysis JSON
   - Used for analytics queries

2. **`child_development_trends`** - Daily aggregated trends
   - Pre-aggregated for fast dashboard queries
   - Tracks vocabulary, complexity, scores over time

---

## Integration Flow

```
1. Parent uploads audio → POST /api/analyze-session
2. ElevenLabs STT transcribes audio
3. Gemini analyzes transcript for development insights
4. Data saved to Firebase (real-time access)
5. Data saved to Snowflake (analytics)
6. Dashboard queries GET /api/child-profile for trends
7. Dashboard queries GET /api/adaptive-learning for activities
```

---

## Testing

### Test with Sample Audio

```bash
# Create a test audio file or use existing one
curl -X POST http://localhost:5000/api/analyze-session \
  -H "X-User-ID: test-parent" \
  -F "audio_file=@test_conversation.mp3" \
  -F "child_age=4" \
  -F "child_name=TestChild" \
  -F 'session_context={"duration_minutes": 2}'
```

### Check Health

```bash
curl http://localhost:5000/api/health
```

Should show:
- ✅ Gemini: available
- ✅ ElevenLabs: available
- ✅ Firebase: available (if configured)
- ✅ Snowflake: available (if configured)

---

## Error Handling

All endpoints return standard error responses:

```json
{
  "error": "Error message here"
}
```

Common errors:
- `400`: Missing required fields (child_age, audio_file)
- `500`: Service unavailable (Gemini, ElevenLabs, etc.)

---

## Next Steps

1. **Test the endpoints** with sample audio
2. **Build the React dashboard** to visualize the data
3. **Add more analysis features** (phonetics, emotion detection)
4. **Create parent-friendly visualizations** (charts, progress bars)

