# HoloMentor Dashboard & Analytics API

## Overview
The dashboard system uses **Snowflake** for analytics and AI-powered insights, with Firebase as a fallback for user profiles.

## API Endpoints

### 1. User Profile Management
**`GET/POST/PUT /api/user/profile`**

Get, create, or update user profile.

**Headers:**
- `X-User-ID`: User identifier (required)

**GET Response:**
```json
{
  "name": "John Doe",
  "age": 15,
  "learning_goals": ["Math", "Science"],
  "preferences": {
    "difficulty_level": "intermediate",
    "voice_id": "default"
  },
  "analytics": {
    "total_interactions": 45,
    "engagement_score": 0.75,
    ...
  }
}
```

**POST/PUT Body:**
```json
{
  "name": "John Doe",
  "age": 15,
  "learning_goals": ["Math", "Science"],
  "preferences": {
    "difficulty_level": "intermediate"
  }
}
```

---

### 2. Dashboard Data
**`GET /api/dashboard`**

Get comprehensive dashboard with AI insights.

**Headers:**
- `X-User-ID`: User identifier (required)

**Query Parameters:**
- `days`: Number of days to analyze (default: 30)

**Response:**
```json
{
  "user_id": "user123",
  "summary": {
    "total_interactions": 45,
    "active_days": 12,
    "engagement_score": 0.75,
    "most_common_emotion": "excited"
  },
  "performance": {
    "avg_response_time": 0.58,
    "avg_audio_duration": 16.8,
    "progress_timeline": [
      {
        "date": "2025-11-08",
        "interactions": 5,
        "avg_time": 0.6
      }
    ]
  },
  "topics": ["photosynthesis", "algebra", "history"],
  "ai_insights": [
    "🌟 Great progress! You've had 45 learning interactions.",
    "⚡ Fast responses show you're asking great questions!",
    "😊 Your enthusiasm is showing! Keep that energy!"
  ],
  "recommendations": [
    "You're doing great! Consider challenging yourself with more complex topics"
  ],
  "profile": {
    "name": "John Doe",
    "age": 15
  }
}
```

---

### 3. AI Insights
**`GET /api/analytics/insights`**

Get AI-powered insights for a user.

**Headers:**
- `X-User-ID`: User identifier (required)

**Query Parameters:**
- `days`: Number of days to analyze (default: 30)

**Response:**
```json
{
  "total_interactions": 45,
  "avg_response_time": 0.58,
  "avg_audio_duration": 16.8,
  "active_days": 12,
  "most_common_emotion": "excited",
  "topics_covered": ["photosynthesis", "algebra", ...],
  "progress_timeline": [...],
  "engagement_score": 0.75,
  "insights": [
    "🌟 Great progress! You've had 45 learning interactions.",
    "⚡ Fast responses show you're asking great questions!"
  ]
}
```

---

### 4. Conversation History
**`GET /api/analytics/conversations`**

Get conversation history for analytics.

**Headers:**
- `X-User-ID`: User identifier (required)

**Query Parameters:**
- `limit`: Number of conversations to return (default: 50)

**Response:**
```json
{
  "user_id": "user123",
  "conversations": [
    {
      "timestamp": "2025-11-08T04:12:09",
      "question": "What is photosynthesis?",
      "response": "Photosynthesis is...",
      "emotion": "confused"
    }
  ],
  "total": 45
}
```

---

## Data Storage

### Snowflake Tables

1. **`user_interactions`**
   - Stores every chat interaction
   - Tracks: user_input, ai_response, emotion, response_time, audio_duration
   - Used for analytics and insights

2. **`user_profiles`**
   - User profile data
   - Learning goals, preferences, age, name

3. **`learning_analytics`**
   - Daily aggregated analytics
   - Engagement scores, emotion trends, topics covered

### Firebase (Fallback)
- User profiles and conversation history
- Used when Snowflake is not configured

---

## Automatic Data Collection

Every `/api/ask` request automatically:
1. Logs interaction to Snowflake (if configured)
2. Tracks emotion, response time, audio duration
3. Associates with user_id and session_id
4. Enables personalized insights

**Response includes:**
- `interaction_id`: Unique ID for this interaction
- `session_id`: Session identifier (from `X-Session-ID` header or auto-generated)

---

## Setup

### 1. Snowflake Configuration

Add to `.env`:
```bash
SNOWFLAKE_ACCOUNT=your-account.snowflakecomputing.com
SNOWFLAKE_USER=your-username
SNOWFLAKE_PASSWORD=your-password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=HOLOMENTOR
SNOWFLAKE_SCHEMA=ANALYTICS
```

### 2. Install Dependencies
```bash
pip install snowflake-connector-python snowflake-sqlalchemy
```

### 3. Tables Auto-Created
Tables are automatically created on first connection.

---

## Usage in Mobile App

### Example: Get Dashboard
```javascript
// mobile/api.js
export const getDashboard = async (userId) => {
  const response = await fetch(`${API_BASE_URL}/api/dashboard`, {
    headers: {
      'X-User-ID': userId
    }
  });
  return response.json();
};
```

### Example: Update Profile
```javascript
export const updateProfile = async (userId, profileData) => {
  const response = await fetch(`${API_BASE_URL}/api/user/profile`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'X-User-ID': userId
    },
    body: JSON.stringify(profileData)
  });
  return response.json();
};
```

---

## AI Insights Features

The system automatically generates insights like:
- **Progress tracking**: "You've had X interactions"
- **Engagement analysis**: "Your learning activity is increasing"
- **Emotion insights**: "Your enthusiasm is showing!"
- **Performance metrics**: Response times, audio durations
- **Personalized recommendations**: Based on learning patterns

All insights are generated from Snowflake analytics data.

