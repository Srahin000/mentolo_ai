-- ============================================
-- Snowflake Dashboard SQL Queries
-- Curiosity Companion - Child Development Analytics
-- ENRICHED SCHEMA - 3 Months of Data
-- ============================================

-- ============================================
-- TILE 1: Development Scores Over Time
-- CHART TYPE: Line Chart (Multi-line)
-- CONFIG: X-axis = date, Y-axis = all score columns
-- ============================================
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

-- ============================================
-- TILE 2: Vocabulary Growth
-- CHART TYPE: Line Chart (Multi-line)
-- CONFIG: X-axis = date, Y-axis = vocabulary_size, sentence_complexity
-- ============================================
SELECT 
    DATE(date) as date,
    vocabulary_size,
    sentence_complexity
FROM child_development_trends
WHERE child_id = 'demo_child_tommy'
ORDER BY date ASC;

-- ============================================
-- TILE 3: Current Development Scores
-- CHART TYPE: Bar Chart (Horizontal or Vertical)
-- CONFIG: X-axis = development_area, Y-axis = score
-- IMPORTANT: Set chart type to "Bar Chart" in Snowflake UI
-- ============================================
SELECT 
    'Language' as development_area,
    language_score as score
FROM child_development_trends
WHERE child_id = 'demo_child_tommy'
ORDER BY date DESC
LIMIT 1

UNION ALL

SELECT 
    'Cognitive',
    cognitive_score
FROM child_development_trends
WHERE child_id = 'demo_child_tommy'
ORDER BY date DESC
LIMIT 1

UNION ALL

SELECT 
    'Emotional',
    emotional_score
FROM child_development_trends
WHERE child_id = 'demo_child_tommy'
ORDER BY date DESC
LIMIT 1

UNION ALL

SELECT 
    'Social',
    social_score
FROM child_development_trends
WHERE child_id = 'demo_child_tommy'
ORDER BY date DESC
LIMIT 1

UNION ALL

SELECT 
    'Creativity',
    creativity_score
FROM child_development_trends
WHERE child_id = 'demo_child_tommy'
ORDER BY date DESC
LIMIT 1;

-- ============================================
-- TILE 4: Session Activity Metrics
-- CHART TYPE: Scorecard (3 separate tiles or single scorecard)
-- CONFIG: Each metric as a separate number display
-- IMPORTANT: Use "Scorecard" visualization type
-- ============================================
SELECT 
    COUNT(DISTINCT session_id) as total_sessions,
    COUNT(DISTINCT DATE(timestamp)) as active_days,
    ROUND(COUNT(DISTINCT DATE(timestamp)) / 30.0 * 100, 1) as consistency_percentage
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
AND timestamp >= DATEADD(day, -30, CURRENT_TIMESTAMP());

-- ============================================
-- TILE 5: Question Frequency & Curiosity
-- CHART TYPE: Line Chart (Multi-line)
-- CONFIG: X-axis = date, Y-axis = question_frequency, curiosity_score
-- ============================================
SELECT 
    DATE(date) as date,
    question_frequency,
    curiosity_score
FROM child_development_trends
WHERE child_id = 'demo_child_tommy'
ORDER BY date ASC;

-- ============================================
-- TILE 6: Recent Sessions (Table)
-- ============================================
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

-- ============================================
-- TILE 7: Overall Development Progress
-- CHART TYPE: Area Chart
-- CONFIG: X-axis = date, Y-axis = overall_score
-- IMPORTANT: Set chart type to "Area Chart" in Snowflake UI
-- ============================================
SELECT 
    DATE(date) as date,
    (language_score + cognitive_score + emotional_score + social_score + creativity_score) / 5.0 as overall_score
FROM child_development_trends
WHERE child_id = 'demo_child_tommy'
ORDER BY date ASC;

-- ============================================
-- TILE 8: Strengths Distribution
-- CHART TYPE: Pie Chart or Donut Chart
-- CONFIG: Category = strength, Value = frequency
-- IMPORTANT: Set chart type to "Pie Chart" in Snowflake UI
-- ============================================
SELECT 
    value as strength,
    COUNT(*) as frequency
FROM child_development_trends,
LATERAL FLATTEN(INPUT => PARSE_JSON(strengths_detected))
WHERE child_id = 'demo_child_tommy'
GROUP BY value
ORDER BY frequency DESC;

-- ============================================
-- UTILITY QUERIES
-- ============================================

-- List all available child IDs
SELECT DISTINCT child_id 
FROM child_development_trends
ORDER BY child_id;

-- Get date range for a child
SELECT 
    MIN(date) as first_date,
    MAX(date) as last_date,
    COUNT(DISTINCT date) as days_tracked
FROM child_development_trends
WHERE child_id = 'demo_child_tommy';

-- Get latest session details
SELECT 
    session_id,
    child_name,
    DATE(timestamp) as session_date,
    LENGTH(transcript) as transcript_length
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
ORDER BY timestamp DESC
LIMIT 1;

-- ============================================
-- FILTERED QUERY (Last 90 Days - 3 Months)
-- ============================================
-- Option 1: Last 90 days (automatic)
SELECT 
    DATE(date) as date,
    language_score,
    vocabulary_size,
    question_frequency
FROM child_development_trends
WHERE child_id = 'demo_child_tommy'
AND date >= DATEADD(day, -90, CURRENT_DATE())
AND date <= CURRENT_DATE()
ORDER BY date ASC;

-- Option 2: Specific date range (uncomment and customize)
-- SELECT 
--     DATE(date) as date,
--     language_score,
--     vocabulary_size,
--     question_frequency
-- FROM child_development_trends
-- WHERE child_id = 'demo_child_tommy'
-- AND date >= '2025-08-01'  -- Replace with your start date
-- AND date <= '2025-11-08'  -- Replace with your end date
-- ORDER BY date ASC;

-- ============================================
-- ENRICHED QUERIES (Using New Columns)
-- ============================================

-- TILE 9: Engagement Metrics Over Time
-- CHART TYPE: Line Chart (Multi-line) or Bar Chart (Grouped)
-- CONFIG: X-axis = session_date, Y-axis = duration_minutes, conversation_turns, child_initiated_topics
SELECT 
    DATE(timestamp) as session_date,
    session_duration / 60.0 as duration_minutes,
    conversation_turns,
    child_initiated_topics
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
ORDER BY timestamp ASC;

-- TILE 10: Grammar Accuracy Trend
-- CHART TYPE: Line Chart (Multi-line)
-- CONFIG: X-axis = session_date, Y-axis = grammar_accuracy, sentence_complexity
SELECT 
    DATE(timestamp) as session_date,
    grammar_accuracy,
    sentence_complexity
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
ORDER BY timestamp ASC;

-- TILE 11: Emotional Intelligence Growth
-- CHART TYPE: Area Chart (Stacked) or Line Chart
-- CONFIG: X-axis = session_date, Y-axis = emotion_words_used, empathy_indicators, emotional_score
-- IMPORTANT: Set chart type to "Area Chart" for stacked visualization
SELECT 
    DATE(timestamp) as session_date,
    emotion_words_used,
    empathy_indicators,
    emotional_score
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
ORDER BY timestamp ASC;

-- TILE 12: Cognitive Patterns
-- CHART TYPE: Bar Chart (Grouped) or Line Chart
-- CONFIG: X-axis = session_date, Y-axis = reasoning_language_count, abstract_thinking_score, curiosity_score
-- IMPORTANT: Set chart type to "Bar Chart" for grouped bars
SELECT 
    DATE(timestamp) as session_date,
    reasoning_language_count,
    abstract_thinking_score,
    curiosity_score
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
ORDER BY timestamp DESC
LIMIT 30;

-- TILE 13: Top Strengths Distribution
-- CHART TYPE: Pie Chart or Donut Chart
-- CONFIG: Category = top_strength, Value = frequency
-- IMPORTANT: Set chart type to "Pie Chart" in Snowflake UI
SELECT 
    top_strength,
    COUNT(*) as frequency
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
AND top_strength IS NOT NULL
GROUP BY top_strength
ORDER BY frequency DESC;

-- TILE 14: Growth Areas Focus
-- CHART TYPE: Bar Chart (Horizontal recommended)
-- CONFIG: X-axis = growth_area, Y-axis = sessions_mentioned
-- IMPORTANT: Set chart type to "Bar Chart" and consider horizontal orientation
SELECT 
    growth_area,
    COUNT(*) as sessions_mentioned
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
AND growth_area IS NOT NULL
GROUP BY growth_area
ORDER BY sessions_mentioned DESC;

-- TILE 15: Session Quality Scorecard
-- CHART TYPE: Scorecard (4 separate metrics)
-- CONFIG: Each column as a separate number display
-- IMPORTANT: Use "Scorecard" visualization type or create 4 separate tiles
SELECT 
    AVG(session_duration) / 60.0 as avg_duration_minutes,
    AVG(conversation_turns) as avg_turns,
    AVG(child_initiated_topics) as avg_child_topics,
    AVG(question_frequency) as avg_questions
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
AND timestamp >= DATEADD(day, -90, CURRENT_TIMESTAMP());

-- TILE 16: Comprehensive Development Overview (Table)
SELECT 
    DATE(timestamp) as session_date,
    language_score,
    cognitive_score,
    emotional_score,
    social_score,
    creativity_score,
    vocabulary_size,
    question_frequency,
    top_strength,
    growth_area
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
ORDER BY timestamp DESC
LIMIT 20;

