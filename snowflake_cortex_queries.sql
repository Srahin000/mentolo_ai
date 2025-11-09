-- ============================================
-- Snowflake Cortex AI Queries for Hackathon Dashboard
-- Curiosity Companion - Child Development Analytics
-- ============================================
-- These queries use Cortex AI for advanced insights
-- Add these as tiles to your Snowflake dashboard
-- ============================================

-- ============================================
-- TILE 9: Cortex AI Daily Insight
-- CHART TYPE: Text/HTML Card
-- CONFIG: Display as formatted text, large font
-- ============================================
SELECT 
    SNOWFLAKE.CORTEX.COMPLETE(
        'snowflake-arctic',
        CONCAT(
            'Analyze this child development data and provide a compelling daily insight for parents. ',
            'Focus on the most significant development this week. Be specific and encouraging. ',
            'Data: ',
            (
                SELECT JSON_OBJECT(
                    'total_sessions': COUNT(*),
                    'avg_language': AVG(language_score),
                    'avg_cognitive': AVG(cognitive_score),
                    'avg_emotional': AVG(emotional_score),
                    'vocabulary_growth': MAX(vocabulary_size) - MIN(vocabulary_size),
                    'recent_strength': MODE(top_strength),
                    'growth_area': MODE(growth_area)
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

-- ============================================
-- TILE 10: Cortex Pattern Detection
-- CHART TYPE: Text/HTML Card
-- CONFIG: Display as formatted insights with bullet points
-- ============================================
SELECT 
    SNOWFLAKE.CORTEX.COMPLETE(
        'snowflake-arctic',
        CONCAT(
            'Detect patterns in this child development data. Identify: ',
            '1. Correlations between development areas (e.g., does high language correlate with high cognitive?), ',
            '2. Temporal patterns (e.g., are scores higher on certain days of week?), ',
            '3. Anomalies or outliers that need attention. ',
            'Format as JSON with keys: correlations, temporal_patterns, anomalies. ',
            'Data: ',
            (
                SELECT JSON_OBJECT(
                    'sessions': ARRAY_AGG(
                        JSON_OBJECT(
                            'date': DATE(timestamp),
                            'day_of_week': DAYNAME(timestamp),
                            'language': language_score,
                            'cognitive': cognitive_score,
                            'emotional': emotional_score,
                            'social': social_score,
                            'creativity': creativity_score,
                            'vocabulary': vocabulary_size,
                            'complexity': sentence_complexity
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

-- ============================================
-- TILE 11: Cortex Predictive Analytics
-- CHART TYPE: Text/HTML Card
-- CONFIG: Display as formatted predictions
-- ============================================
SELECT 
    SNOWFLAKE.CORTEX.COMPLETE(
        'snowflake-arctic',
        CONCAT(
            'Based on this child development trajectory, predict future development over the next 3 months. ',
            'Provide: 1) Expected growth areas, 2) Potential challenges, 3) Specific recommendations. ',
            'Be realistic and actionable. ',
            'Data: ',
            (
                SELECT JSON_OBJECT(
                    'current_age': 4,
                    'trajectory': ARRAY_AGG(
                        JSON_OBJECT(
                            'date': DATE(timestamp),
                            'language': language_score,
                            'cognitive': cognitive_score,
                            'emotional': emotional_score,
                            'social': social_score,
                            'creativity': creativity_score,
                            'vocabulary': vocabulary_size,
                            'complexity': sentence_complexity
                        ) ORDER BY timestamp
                    ),
                    'recent_trend': CASE 
                        WHEN AVG(CASE WHEN timestamp >= DATEADD(day, -14, CURRENT_TIMESTAMP()) THEN language_score END) > 
                             AVG(CASE WHEN timestamp < DATEADD(day, -14, CURRENT_TIMESTAMP()) THEN language_score END)
                        THEN 'improving' ELSE 'stable' END
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

-- ============================================
-- TILE 12: Cortex Benchmark Comparison
-- CHART TYPE: Text/HTML Card
-- CONFIG: Display as comparison table
-- ============================================
SELECT 
    SNOWFLAKE.CORTEX.COMPLETE(
        'snowflake-arctic',
        CONCAT(
            'Compare this 4-year-old child development to age-appropriate benchmarks. ',
            'Current scores (last 30 days): ',
            (
                SELECT JSON_OBJECT(
                    'language': AVG(language_score),
                    'cognitive': AVG(cognitive_score),
                    'emotional': AVG(emotional_score),
                    'social': AVG(social_score),
                    'creativity': AVG(creativity_score),
                    'vocabulary': AVG(vocabulary_size),
                    'complexity': AVG(sentence_complexity)
                )
                FROM child_development_sessions
                WHERE child_id = 'demo_child_tommy'
                AND timestamp >= DATEADD(day, -30, CURRENT_TIMESTAMP())
            )::STRING,
            '. Age 4 benchmarks: language=70, cognitive=65, emotional=68, social=70, creativity=72, vocabulary=800, complexity=4.5. ',
            'Provide: 1) Areas ahead of benchmark, 2) Areas on track, 3) Areas needing support, 4) Specific recommendations for each area.'
        )
    ) as benchmark_analysis
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
LIMIT 1;

-- ============================================
-- TILE 13: Interactive Chatbot - Trend Analysis
-- CHART TYPE: Text/HTML Card
-- CONFIG: Display as Q&A format
-- NOTE: Requires Cortex Analyst (may not work in all regions)
-- ============================================
-- Question: "What are the main trends in language development over the past 3 months?"
SELECT 
    SNOWFLAKE.CORTEX.ANALYZE(
        'What are the main trends in language development over the past 3 months? Identify growth patterns, improvements, and areas of concern.',
        'SELECT 
            DATE(timestamp) as date,
            language_score,
            vocabulary_size,
            sentence_complexity,
            grammar_accuracy,
            question_frequency
        FROM child_development_sessions
        WHERE child_id = ''demo_child_tommy''
        AND timestamp >= DATEADD(day, -90, CURRENT_TIMESTAMP())
        ORDER BY timestamp ASC',
        ARRAY_CONSTRUCT()
    ) as answer;

-- ============================================
-- TILE 14: Interactive Chatbot - Emotional Intelligence
-- CHART TYPE: Text/HTML Card
-- ============================================
-- Question: "How has emotional intelligence changed over time?"
SELECT 
    SNOWFLAKE.CORTEX.ANALYZE(
        'How has emotional intelligence changed over time? Analyze trends in emotional development, empathy indicators, and emotion vocabulary.',
        'SELECT 
            DATE(timestamp) as date,
            emotional_score,
            emotion_words_used,
            empathy_indicators,
            daily_insight
        FROM child_development_sessions
        WHERE child_id = ''demo_child_tommy''
        ORDER BY timestamp ASC',
        ARRAY_CONSTRUCT()
    ) as answer;

-- ============================================
-- TILE 15: Interactive Chatbot - Activity Recommendations
-- CHART TYPE: Text/HTML Card
-- ============================================
-- Question: "What activities would help improve cognitive scores?"
SELECT 
    SNOWFLAKE.CORTEX.ANALYZE(
        'What activities would help improve cognitive development based on current patterns? Consider reasoning language, abstract thinking, and curiosity scores.',
        'SELECT 
            cognitive_score,
            reasoning_language_count,
            abstract_thinking_score,
            curiosity_score,
            top_strength,
            growth_area,
            suggested_activity
        FROM child_development_sessions
        WHERE child_id = ''demo_child_tommy''
        ORDER BY timestamp DESC
        LIMIT 10',
        ARRAY_CONSTRUCT()
    ) as answer;

-- ============================================
-- TILE 16: Interactive Chatbot - Peer Comparison
-- CHART TYPE: Text/HTML Card
-- ============================================
-- Question: "How does this child compare to typical 4-year-old development?"
SELECT 
    SNOWFLAKE.CORTEX.ANALYZE(
        'How does this child compare to typical 4-year-old development benchmarks? Provide specific comparisons and identify areas of strength and areas needing support.',
        'SELECT 
            AVG(language_score) as avg_language,
            AVG(cognitive_score) as avg_cognitive,
            AVG(emotional_score) as avg_emotional,
            AVG(social_score) as avg_social,
            AVG(creativity_score) as avg_creativity,
            AVG(vocabulary_size) as avg_vocabulary,
            AVG(sentence_complexity) as avg_complexity,
            MAX(vocabulary_size) as max_vocabulary,
            MAX(sentence_complexity) as max_complexity
        FROM child_development_sessions
        WHERE child_id = ''demo_child_tommy''
        AND timestamp >= DATEADD(day, -30, CURRENT_TIMESTAMP())',
        ARRAY_CONSTRUCT()
    ) as answer;

-- ============================================
-- TILE 17: Data Pipeline Status
-- CHART TYPE: Gauge/Status Cards
-- CONFIG: Multiple small cards showing metrics
-- ============================================
SELECT 
    COUNT(*) as sessions_today,
    MAX(timestamp) as last_session,
    COUNT(DISTINCT DATE(timestamp)) as active_days_last_30,
    AVG(session_duration) as avg_session_duration_seconds,
    SUM(session_duration) / 60.0 as total_minutes_last_30_days
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
AND timestamp >= DATEADD(day, -30, CURRENT_TIMESTAMP());

-- ============================================
-- TILE 18: Data Quality Metrics
-- CHART TYPE: Bar Chart
-- CONFIG: Horizontal bars showing completeness
-- ============================================
SELECT 
    'Complete Sessions' as metric,
    COUNT(*) as value,
    'Sessions with transcript and analysis' as description
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
AND transcript IS NOT NULL
AND analysis IS NOT NULL

UNION ALL

SELECT 
    'Sessions with Scores' as metric,
    COUNT(*) as value,
    'Sessions with all development scores' as description
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
AND language_score IS NOT NULL
AND cognitive_score IS NOT NULL
AND emotional_score IS NOT NULL

UNION ALL

SELECT 
    'Enriched Sessions' as metric,
    COUNT(*) as value,
    'Sessions with enriched columns (curiosity, empathy, etc.)' as description
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
AND curiosity_score IS NOT NULL
AND empathy_indicators IS NOT NULL;

-- ============================================
-- TILE 19: Cortex Strength Analysis
-- CHART TYPE: Text/HTML Card
-- ============================================
SELECT 
    SNOWFLAKE.CORTEX.COMPLETE(
        'snowflake-arctic',
        CONCAT(
            'Analyze this child strengths and provide a comprehensive strength profile. ',
            'Identify: 1) Top 3 consistent strengths, 2) Emerging strengths, 3) How to nurture each strength. ',
            'Data: ',
            (
                SELECT JSON_OBJECT(
                    'strengths': ARRAY_AGG(DISTINCT top_strength),
                    'strength_frequency': OBJECT_CONSTRUCT(
                        MODE(top_strength), COUNT(*)
                    ),
                    'recent_strengths': ARRAY_AGG(
                        top_strength ORDER BY timestamp DESC LIMIT 5
                    )
                )
                FROM child_development_sessions
                WHERE child_id = 'demo_child_tommy'
                AND top_strength IS NOT NULL
            )::STRING
        )
    ) as strength_analysis
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
LIMIT 1;

-- ============================================
-- TILE 20: Cortex Growth Recommendations
-- CHART TYPE: Text/HTML Card
-- ============================================
SELECT 
    SNOWFLAKE.CORTEX.COMPLETE(
        'snowflake-arctic',
        CONCAT(
            'Based on this child development data, provide specific, actionable recommendations for growth. ',
            'Focus on: 1) Activities to try, 2) Skills to practice, 3) Milestones to work toward. ',
            'Data: ',
            (
                SELECT JSON_OBJECT(
                    'growth_areas': ARRAY_AGG(DISTINCT growth_area),
                    'current_scores': JSON_OBJECT(
                        'language': AVG(language_score),
                        'cognitive': AVG(cognitive_score),
                        'emotional': AVG(emotional_score),
                        'social': AVG(social_score),
                        'creativity': AVG(creativity_score)
                    ),
                    'suggested_activities': ARRAY_AGG(DISTINCT suggested_activity)
                )
                FROM child_development_sessions
                WHERE child_id = 'demo_child_tommy'
                AND timestamp >= DATEADD(day, -30, CURRENT_TIMESTAMP())
            )::STRING
        )
    ) as recommendations
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
LIMIT 1;

-- ============================================
-- NOTES FOR HACKATHON:
-- ============================================
-- 1. Test each Cortex query individually first
-- 2. If Cortex Analyst unavailable, use Cortex Complete with pre-defined queries
-- 3. Format text tiles as HTML for better display
-- 4. Add refresh intervals (5-10 minutes) for real-time feel
-- 5. Create backup queries if Cortex unavailable
-- 6. Document which features work in your region
-- ============================================

