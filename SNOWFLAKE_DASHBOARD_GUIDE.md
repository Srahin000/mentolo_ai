# 📊 Snowflake Dashboard Guide

## How to Build a Dashboard in Snowflake

### Step-by-Step Process

1. **Click "New Tile"** button in your dashboard
2. **Write SQL Query** in the SQL editor
3. **Run Query** to see results
4. **Click "Chart"** to visualize the data
5. **Save Tile** by selecting "Return to dashboard"
6. **Repeat** to add more tiles

---

## 📈 Recommended Dashboard Tiles

### Tile 1: Daily Development Scores (Line Chart)

**Purpose**: Show language, cognitive, emotional, social, and creativity scores over time

```sql
SELECT 
    DATE(date) as date,
    language_score,
    cognitive_score,
    emotional_score,
    social_score,
    creativity_score
FROM child_development_trends
WHERE child_id = 'demo_child_tommy'
ORDER BY date ASC;
```

**Visualization**: Line Chart
- X-axis: Date
- Y-axis: Score (0-100)
- Multiple lines for each development area

---

### Tile 2: Vocabulary Growth (Line Chart)

**Purpose**: Track vocabulary size progression

```sql
SELECT 
    DATE(date) as date,
    vocabulary_size,
    sentence_complexity
FROM child_development_trends
WHERE child_id = 'demo_child_tommy'
ORDER BY date ASC;
```

**Visualization**: Line Chart
- X-axis: Date
- Y-axis: Vocabulary Size / Sentence Complexity

---

### Tile 3: Development Area Comparison (Bar Chart)

**Purpose**: Compare current scores across all development areas

```sql
SELECT 
    'Language' as area,
    language_score as score
FROM child_development_trends
WHERE child_id = 'demo_child_tommy'
ORDER BY date DESC
LIMIT 1

UNION ALL

SELECT 
    'Cognitive' as area,
    cognitive_score as score
FROM child_development_trends
WHERE child_id = 'demo_child_tommy'
ORDER BY date DESC
LIMIT 1

UNION ALL

SELECT 
    'Emotional' as area,
    emotional_score as score
FROM child_development_trends
WHERE child_id = 'demo_child_tommy'
ORDER BY date DESC
LIMIT 1

UNION ALL

SELECT 
    'Social' as area,
    social_score as score
FROM child_development_trends
WHERE child_id = 'demo_child_tommy'
ORDER BY date DESC
LIMIT 1

UNION ALL

SELECT 
    'Creativity' as area,
    creativity_score as score
FROM child_development_trends
WHERE child_id = 'demo_child_tommy'
ORDER BY date DESC
LIMIT 1;
```

**Visualization**: Bar Chart
- X-axis: Development Area
- Y-axis: Score

---

### Tile 4: Session Activity (Scorecard)

**Purpose**: Show total sessions and consistency

```sql
SELECT 
    COUNT(DISTINCT session_id) as total_sessions,
    COUNT(DISTINCT DATE(timestamp)) as active_days,
    ROUND(COUNT(DISTINCT DATE(timestamp)) / 30.0 * 100, 1) as consistency_percentage
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
AND timestamp >= DATEADD(day, -30, CURRENT_TIMESTAMP());
```

**Visualization**: Scorecard (3 metrics)

---

### Tile 5: Question Frequency Trend (Line Chart)

**Purpose**: Track curiosity and engagement

```sql
SELECT 
    DATE(date) as date,
    question_frequency,
    curiosity_score
FROM child_development_trends
WHERE child_id = 'demo_child_tommy'
ORDER BY date ASC;
```

**Visualization**: Line Chart
- X-axis: Date
- Y-axis: Question Frequency / Curiosity Score

---

### Tile 6: Recent Sessions Summary (Table)

**Purpose**: Show latest session details

```sql
SELECT 
    DATE(timestamp) as session_date,
    child_name,
    child_age,
    LENGTH(transcript) as transcript_length,
    JSON_EXTRACT_PATH_TEXT(analysis, 'development_snapshot', 'language', 'score') as language_score
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
ORDER BY timestamp DESC
LIMIT 10;
```

**Visualization**: Table

---

### Tile 7: Development Progress (Area Chart)

**Purpose**: Show overall development trajectory

```sql
SELECT 
    DATE(date) as date,
    (language_score + cognitive_score + emotional_score + social_score + creativity_score) / 5.0 as overall_score
FROM child_development_trends
WHERE child_id = 'demo_child_tommy'
ORDER BY date ASC;
```

**Visualization**: Area Chart
- X-axis: Date
- Y-axis: Overall Score

---

### Tile 8: Strengths Detected (Pie Chart)

**Purpose**: Show distribution of strengths

```sql
SELECT 
    value as strength,
    COUNT(*) as frequency
FROM child_development_trends,
LATERAL FLATTEN(INPUT => PARSE_JSON(strengths_detected))
WHERE child_id = 'demo_child_tommy'
GROUP BY value
ORDER BY frequency DESC;
```

**Visualization**: Pie Chart

---

## 🎯 Quick Start Queries

### For Any Child ID

Replace `'demo_child_tommy'` with any child ID:

```sql
-- Get all available child IDs
SELECT DISTINCT child_id 
FROM child_development_trends
ORDER BY child_id;
```

### Filter by Date Range

```sql
SELECT 
    DATE(date) as date,
    language_score,
    vocabulary_size
FROM child_development_trends
WHERE child_id = 'demo_child_tommy'
AND date >= '2025-10-01'
AND date <= '2025-11-08'
ORDER BY date ASC;
```

---

## 📋 Dashboard Layout Suggestions

### Layout 1: Overview Dashboard
1. **Top Row**: Scorecard (Total Sessions, Active Days, Consistency)
2. **Middle Row**: Line Chart (Development Scores Over Time)
3. **Bottom Row**: Bar Chart (Current Scores Comparison)

### Layout 2: Detailed Analytics
1. **Top**: Vocabulary Growth Line Chart
2. **Middle Left**: Development Area Comparison Bar Chart
3. **Middle Right**: Question Frequency Line Chart
4. **Bottom**: Recent Sessions Table

### Layout 3: Executive Summary
1. **Top**: Overall Progress Area Chart
2. **Middle**: Strengths Pie Chart
3. **Bottom**: Development Scores Line Chart

---

## 🔧 Tips for Building Dashboards

1. **Start Simple**: Begin with 2-3 tiles, then add more
2. **Use Filters**: Add date range filters for flexibility
3. **Color Coding**: Use consistent colors for development areas
4. **Refresh Settings**: Set auto-refresh for real-time data
5. **Share Access**: Share dashboard with team members

---

## 🎨 Visualization Best Practices

- **Line Charts**: For trends over time (vocabulary, scores)
- **Bar Charts**: For comparisons (current scores, areas)
- **Pie Charts**: For distributions (strengths, categories)
- **Area Charts**: For cumulative progress
- **Scorecards**: For key metrics (sessions, consistency)
- **Tables**: For detailed data (session list)

---

## 📊 Example: Complete Dashboard Query

If you want a single query that shows everything:

```sql
SELECT 
    t.date,
    t.language_score,
    t.cognitive_score,
    t.vocabulary_size,
    t.question_frequency,
    COUNT(DISTINCT s.session_id) as sessions_today
FROM child_development_trends t
LEFT JOIN child_development_sessions s 
    ON DATE(s.timestamp) = t.date 
    AND s.child_id = t.child_id
WHERE t.child_id = 'demo_child_tommy'
GROUP BY t.date, t.language_score, t.cognitive_score, t.vocabulary_size, t.question_frequency
ORDER BY t.date ASC;
```

---

## 🚀 Next Steps

1. **Create your first tile** using Tile 1 (Development Scores)
2. **Add more tiles** one at a time
3. **Arrange tiles** by dragging and dropping
4. **Save dashboard** with a meaningful name
5. **Share** with your team

---

**Happy Dashboard Building!** 📊✨

