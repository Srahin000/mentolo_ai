# Snowflake Hackathon Dashboard - Complete Guide

## 🏆 Hackathon Strategy: Maximize Snowflake Features

This guide helps you build a **Snowflake-native dashboard** that showcases:
- ✅ **Snowflake Native Dashboards** (built-in visualization)
- ✅ **Cortex AI** (LLM functions, Analyst, Search)
- ✅ **Real-time Analytics** (live data queries)
- ✅ **Data Pipeline** (ingestion → transformation → insights)
- ✅ **Interactive Chatbot** (Cortex Analyst for natural language queries)

---

## 🎯 Dashboard Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              SNOWFLAKE NATIVE DASHBOARD                      │
│  (Built using Snowflake's built-in dashboard feature)        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  TILE 1-8: Standard Visualizations                          │
│  - Development scores over time                              │
│  - Vocabulary growth                                         │
│  - Engagement metrics                                        │
│  - Emotional intelligence trends                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  TILE 9-12: Cortex AI Insights                               │
│  - AI-generated insights using Cortex Complete               │
│  - Pattern detection                                         │
│  - Predictive analytics                                       │
│  - Benchmark comparisons                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  TILE 13-16: Interactive Chatbot                             │
│  - Natural language queries (Cortex Analyst)                 │
│  - "What are the main trends?"                               │
│  - "How is language developing?"                           │
│  - "What activities would help?"                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Step 1: Create Snowflake Dashboard

### In Snowflake UI:

1. **Navigate to Dashboards**
   - Click "Dashboards" in left sidebar
   - Click "Create Dashboard"
   - Name: "Curiosity Companion - Child Development Analytics"

2. **Add Tiles from SQL Queries**
   - Use queries from `snowflake_dashboard_queries.sql`
   - Each query becomes a tile
   - Configure chart types (see `SNOWFLAKE_CHART_CONFIGURATION.md`)

---

## 🤖 Step 2: Add Cortex AI Insights Tiles

### Tile 9: AI-Generated Daily Insight

```sql
-- TILE 9: Cortex AI Daily Insight
-- CHART TYPE: Text/HTML
-- CONFIG: Display as formatted text card

SELECT 
    SNOWFLAKE.CORTEX.COMPLETE(
        'snowflake-arctic',
        CONCAT(
            'Analyze this child development data and provide a compelling daily insight for parents. ',
            'Focus on the most significant development this week. ',
            'Data: ',
            (
                SELECT JSON_OBJECT(
                    'total_sessions': COUNT(*),
                    'avg_language': AVG(language_score),
                    'avg_cognitive': AVG(cognitive_score),
                    'vocabulary_growth': MAX(vocabulary_size) - MIN(vocabulary_size),
                    'recent_strength': MODE(top_strength)
                )
                FROM child_development_sessions
                WHERE child_id = 'demo_child_tommy'
                AND timestamp >= DATEADD(day, -7, CURRENT_TIMESTAMP())
            )::STRING
        )
    ) as daily_insight
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
LIMIT 1;
```

### Tile 10: Pattern Detection

```sql
-- TILE 10: Cortex Pattern Detection
-- CHART TYPE: Text/HTML
-- CONFIG: Display as formatted insights

SELECT 
    SNOWFLAKE.CORTEX.COMPLETE(
        'snowflake-arctic',
        CONCAT(
            'Detect patterns in this child development data. Identify: ',
            '1. Correlations between development areas, ',
            '2. Temporal patterns (e.g., higher scores on certain days), ',
            '3. Anomalies that need attention. ',
            'Data: ',
            (
                SELECT JSON_OBJECT(
                    'sessions': ARRAY_AGG(
                        JSON_OBJECT(
                            'date': DATE(timestamp),
                            'language': language_score,
                            'cognitive': cognitive_score,
                            'emotional': emotional_score,
                            'social': social_score,
                            'creativity': creativity_score
                        ) ORDER BY timestamp
                    )
                )
                FROM child_development_sessions
                WHERE child_id = 'demo_child_tommy'
                ORDER BY timestamp ASC
            )::STRING
        )
    ) as patterns
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
LIMIT 1;
```

### Tile 11: Predictive Insights

```sql
-- TILE 11: Cortex Predictive Analytics
-- CHART TYPE: Text/HTML

SELECT 
    SNOWFLAKE.CORTEX.COMPLETE(
        'snowflake-arctic',
        CONCAT(
            'Based on this child development trajectory, predict future development. ',
            'Provide: 1) Expected growth areas, 2) Potential challenges, 3) Recommendations. ',
            'Data: ',
            (
                SELECT JSON_OBJECT(
                    'trajectory': ARRAY_AGG(
                        JSON_OBJECT(
                            'date': DATE(timestamp),
                            'language': language_score,
                            'cognitive': cognitive_score,
                            'vocabulary': vocabulary_size
                        ) ORDER BY timestamp
                    )
                )
                FROM child_development_sessions
                WHERE child_id = 'demo_child_tommy'
                ORDER BY timestamp ASC
            )::STRING
        )
    ) as predictions
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
LIMIT 1;
```

### Tile 12: Benchmark Comparison

```sql
-- TILE 12: Cortex Benchmark Analysis
-- CHART TYPE: Text/HTML

SELECT 
    SNOWFLAKE.CORTEX.COMPLETE(
        'snowflake-arctic',
        CONCAT(
            'Compare this 4-year-old child development to age-appropriate benchmarks. ',
            'Current scores: ',
            (
                SELECT JSON_OBJECT(
                    'language': AVG(language_score),
                    'cognitive': AVG(cognitive_score),
                    'vocabulary': AVG(vocabulary_size),
                    'complexity': AVG(sentence_complexity)
                )
                FROM child_development_sessions
                WHERE child_id = 'demo_child_tommy'
                AND timestamp >= DATEADD(day, -30, CURRENT_TIMESTAMP())
            )::STRING,
            '. Age benchmarks: language=70, cognitive=65, vocabulary=800, complexity=4.5. ',
            'Provide comparison and recommendations.'
        )
    ) as benchmark_analysis
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
LIMIT 1;
```

---

## 💬 Step 3: Interactive Chatbot with Cortex Analyst

### Create Chatbot Query Tile

```sql
-- TILE 13: Interactive Chatbot (Cortex Analyst)
-- CHART TYPE: Text/HTML (with input field)
-- NOTE: This requires Cortex Analyst feature

-- Example Query 1: "What are the main trends in language development?"
SELECT 
    SNOWFLAKE.CORTEX.ANALYZE(
        'What are the main trends in language development over the past 3 months?',
        'SELECT 
            DATE(timestamp) as date,
            language_score,
            vocabulary_size,
            sentence_complexity,
            grammar_accuracy
        FROM child_development_sessions
        WHERE child_id = ''demo_child_tommy''
        AND timestamp >= DATEADD(day, -90, CURRENT_TIMESTAMP())
        ORDER BY timestamp ASC',
        ARRAY_CONSTRUCT()
    ) as answer;
```

### Pre-defined Chatbot Queries

Create multiple tiles for common questions:

**Query 2: "How has emotional intelligence changed?"**
```sql
SELECT 
    SNOWFLAKE.CORTEX.ANALYZE(
        'How has emotional intelligence changed over time?',
        'SELECT 
            DATE(timestamp) as date,
            emotional_score,
            emotion_words_used,
            empathy_indicators
        FROM child_development_sessions
        WHERE child_id = ''demo_child_tommy''
        ORDER BY timestamp ASC',
        ARRAY_CONSTRUCT()
    ) as answer;
```

**Query 3: "What activities would help improve cognitive scores?"**
```sql
SELECT 
    SNOWFLAKE.CORTEX.ANALYZE(
        'What activities would help improve cognitive development based on current patterns?',
        'SELECT 
            cognitive_score,
            reasoning_language_count,
            abstract_thinking_score,
            curiosity_score,
            top_strength,
            growth_area
        FROM child_development_sessions
        WHERE child_id = ''demo_child_tommy''
        ORDER BY timestamp DESC
        LIMIT 10',
        ARRAY_CONSTRUCT()
    ) as answer;
```

**Query 4: "Compare to peers"**
```sql
SELECT 
    SNOWFLAKE.CORTEX.ANALYZE(
        'How does this child compare to typical 4-year-old development benchmarks?',
        'SELECT 
            AVG(language_score) as avg_language,
            AVG(cognitive_score) as avg_cognitive,
            AVG(vocabulary_size) as avg_vocabulary,
            AVG(sentence_complexity) as avg_complexity
        FROM child_development_sessions
        WHERE child_id = ''demo_child_tommy''
        AND timestamp >= DATEADD(day, -30, CURRENT_TIMESTAMP())',
        ARRAY_CONSTRUCT()
    ) as answer;
```

---

## 🚀 Step 4: Real-time Data Pipeline Visualization

### Tile 14: Data Pipeline Status

```sql
-- TILE 14: Data Pipeline Status
-- CHART TYPE: Gauge/Status
-- Shows: Sessions ingested today, last update time, data freshness

SELECT 
    COUNT(*) as sessions_today,
    MAX(timestamp) as last_session,
    COUNT(DISTINCT DATE(timestamp)) as active_days_last_30,
    AVG(session_duration) as avg_session_duration
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
AND timestamp >= DATEADD(day, -30, CURRENT_TIMESTAMP());
```

### Tile 15: Data Quality Metrics

```sql
-- TILE 15: Data Quality
-- CHART TYPE: Bar Chart

SELECT 
    'Complete Sessions' as metric,
    COUNT(*) as value
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
AND transcript IS NOT NULL
AND analysis IS NOT NULL

UNION ALL

SELECT 
    'Sessions with Scores' as metric,
    COUNT(*) as value
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
AND language_score IS NOT NULL
AND cognitive_score IS NOT NULL;
```

---

## 🎨 Step 5: Dashboard Layout

### Recommended Layout:

```
┌─────────────────────────────────────────────────────────────┐
│  Row 1: Hero Section                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Daily Insight│  │ Pipeline     │  │ Data Quality │      │
│  │ (Cortex AI)  │  │ Status       │  │ Metrics      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Row 2: Development Trends                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Scores Over  │  │ Vocabulary   │  │ Engagement   │      │
│  │ Time         │  │ Growth       │  │ Metrics      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Row 3: Cortex AI Insights                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Pattern      │  │ Predictive   │  │ Benchmark    │      │
│  │ Detection    │  │ Analytics    │  │ Comparison   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Row 4: Interactive Chatbot                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  "What are the main trends in language development?" │   │
│  │  [Cortex Analyst Answer]                             │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  "How has emotional intelligence changed?"                │   │
│  │  [Cortex Analyst Answer]                             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏆 Hackathon Showcase Points

### 1. **Snowflake Native Features**
- ✅ Built-in dashboard (no external tools)
- ✅ Real-time SQL queries
- ✅ Automatic refresh
- ✅ Shareable dashboards

### 2. **Cortex AI Integration**
- ✅ **Cortex Complete**: AI-generated insights
- ✅ **Cortex Analyst**: Natural language queries
- ✅ **Pattern Detection**: AI-powered analytics
- ✅ **Predictive Analytics**: Future predictions

### 3. **Data Pipeline**
- ✅ Real-time data ingestion
- ✅ Data transformation
- ✅ Enriched analytics
- ✅ Data quality monitoring

### 4. **Interactive Features**
- ✅ Chatbot for natural language queries
- ✅ Dynamic insights
- ✅ Personalized recommendations

---

## 📝 Step 6: Create All SQL Queries

I'll create a comprehensive SQL file with all Cortex AI queries. See `snowflake_cortex_queries.sql`.

---

## 🎯 Demo Script for Judges

### Opening (30 seconds)
"Curiosity Companion uses Snowflake's Cortex AI to provide real-time child development insights. Let me show you..."

### Demo Flow (2 minutes)

1. **Show Standard Dashboard** (30s)
   - "Here's our Snowflake native dashboard with real-time analytics"

2. **Show Cortex AI Insights** (45s)
   - "Cortex AI generates daily insights automatically"
   - "Pattern detection identifies correlations"
   - "Predictive analytics forecasts development"

3. **Show Chatbot** (45s)
   - "Ask questions in natural language"
   - "Cortex Analyst answers based on actual data"
   - "No SQL knowledge needed"

### Closing (30 seconds)
"This showcases Snowflake's Cortex AI capabilities for healthcare analytics, making complex data accessible through natural language."

---

## ✅ Checklist for Hackathon

- [ ] Create Snowflake dashboard
- [ ] Add all 16 tiles (standard + Cortex)
- [ ] Test Cortex AI queries
- [ ] Verify Cortex Analyst works (or have fallback)
- [ ] Create demo script
- [ ] Prepare backup slides
- [ ] Test dashboard sharing
- [ ] Document data pipeline

---

## 🚨 Important Notes

### Cortex Availability

- **Cortex Complete**: Available in most regions
- **Cortex Analyst**: Limited regions (may not work in Australia/Azure)
- **Fallback**: If Analyst unavailable, use Cortex Complete with pre-defined queries

### Testing

1. Test each Cortex query individually
2. Verify dashboard tiles refresh correctly
3. Test chatbot queries
4. Prepare fallback if Cortex unavailable

---

## 📚 Next Steps

1. Run `snowflake_cortex_queries.sql` to create all Cortex tiles
2. Build dashboard in Snowflake UI
3. Test all features
4. Create demo script
5. Practice presentation

This dashboard will showcase the full power of Snowflake + Cortex AI for your hackathon! 🚀

