-- ============================================
-- Snowflake Memory Engine SQL Queries
-- Vector Embeddings & RAG Pipeline
-- "Gemini teaches. Snowflake learns."
-- ============================================

-- ============================================
-- TILE 21: Memory Engine Status
-- CHART TYPE: Status Cards
-- ============================================
SELECT 
    COUNT(*) as total_memories,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT topic) as unique_topics,
    AVG(confidence_score) as avg_confidence
FROM user_embeddings;

-- ============================================
-- TILE 22: Most Discussed Topics (Vector Memory)
-- CHART TYPE: Bar Chart
-- ============================================
SELECT 
    topic,
    COUNT(*) as interaction_count,
    COUNT(DISTINCT user_id) as unique_users,
    AVG(confidence_score) as avg_confidence
FROM user_embeddings
WHERE topic IS NOT NULL
GROUP BY topic
ORDER BY interaction_count DESC
LIMIT 10;

-- ============================================
-- TILE 23: Knowledge Gaps Tracking
-- CHART TYPE: Table or Bar Chart
-- ============================================
SELECT 
    topic,
    concept,
    COUNT(*) as gap_frequency,
    COUNT(DISTINCT user_id) as affected_users,
    MAX(last_mentioned) as last_mentioned
FROM user_knowledge_gaps
WHERE resolved = FALSE
GROUP BY topic, concept
ORDER BY gap_frequency DESC
LIMIT 10;

-- ============================================
-- TILE 24: Learning Summary (Cortex COMPLETE)
-- CHART TYPE: Text/HTML Card
-- ============================================
-- This query generates a personalized learning summary
-- Note: Replace 'demo_user' with actual user_id
SELECT 
    SNOWFLAKE.CORTEX.COMPLETE(
        'snowflake-arctic',
        CONCAT(
            'Generate a personalized learning summary for this student based on their interaction history. ',
            'Include: progress overview, strengths, areas needing attention, and recommendations. ',
            'Data: ',
            (
                SELECT JSON_OBJECT(
                    'total_interactions': COUNT(*),
                    'topics_covered': ARRAY_AGG(DISTINCT topic),
                    'avg_confidence': AVG(confidence_score),
                    'knowledge_gaps': (
                        SELECT ARRAY_AGG(concept)
                        FROM user_knowledge_gaps
                        WHERE user_id = 'demo_user' AND resolved = FALSE
                    )
                )
                FROM user_embeddings
                WHERE user_id = 'demo_user'
            )::STRING
        )
    ) as learning_summary
FROM user_embeddings
WHERE user_id = 'demo_user'
LIMIT 1;

-- ============================================
-- TILE 25: Cohort Analytics (Cortex COMPLETE)
-- CHART TYPE: Text/HTML Card
-- ============================================
SELECT 
    SNOWFLAKE.CORTEX.COMPLETE(
        'snowflake-arctic',
        CONCAT(
            'Analyze learning patterns across all users. Identify: ',
            '1. Which topics are most challenging (low confidence), ',
            '2. Which teaching approaches work best (emotion patterns), ',
            '3. Recommendations for improving learning outcomes. ',
            'Data: ',
            (
                SELECT JSON_OBJECT(
                    'topics': ARRAY_AGG(
                        JSON_OBJECT(
                            'topic': topic,
                            'total_interactions': COUNT(*),
                            'avg_confidence': AVG(confidence_score),
                            'most_common_emotion': MODE(emotion),
                            'unique_users': COUNT(DISTINCT user_id)
                        )
                    )
                )
                FROM user_embeddings
                WHERE topic IS NOT NULL
                GROUP BY topic
            )::STRING
        )
    ) as cohort_analysis
FROM user_embeddings
LIMIT 1;

-- ============================================
-- TILE 26: Vector Similarity Search Example
-- CHART TYPE: Table
-- ============================================
-- Example: Find similar interactions to a question
-- Note: This requires a specific question embedding
-- In practice, this is done via the API endpoint

-- Example query structure:
SELECT 
    question_text,
    answer_text,
    topic,
    emotion,
    timestamp,
    VECTOR_DISTANCE(
        embedding,
        SNOWFLAKE.CORTEX.EMBED_TEXT('snowflake-arctic', 'What is photosynthesis?')
    ) as similarity_score
FROM user_embeddings
WHERE user_id = 'demo_user'
ORDER BY similarity_score ASC
LIMIT 5;

-- ============================================
-- TILE 27: Memory Growth Over Time
-- CHART TYPE: Line Chart
-- ============================================
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as memories_stored,
    COUNT(DISTINCT user_id) as active_users,
    COUNT(DISTINCT topic) as unique_topics
FROM user_embeddings
GROUP BY DATE(timestamp)
ORDER BY date ASC;

-- ============================================
-- TILE 28: Teaching Effectiveness (Cortex Analysis)
-- CHART TYPE: Text/HTML Card
-- ============================================
SELECT 
    SNOWFLAKE.CORTEX.COMPLETE(
        'snowflake-arctic',
        CONCAT(
            'Analyze teaching effectiveness based on interaction data. ',
            'Which teaching tones (emotions) correlate with higher confidence scores? ',
            'Which topics need different teaching approaches? ',
            'Data: ',
            (
                SELECT JSON_OBJECT(
                    'emotion_analysis': ARRAY_AGG(
                        JSON_OBJECT(
                            'emotion': emotion,
                            'avg_confidence': AVG(confidence_score),
                            'interaction_count': COUNT(*)
                        )
                    ),
                    'topic_analysis': ARRAY_AGG(
                        JSON_OBJECT(
                            'topic': topic,
                            'avg_confidence': AVG(confidence_score),
                            'interaction_count': COUNT(*)
                        )
                    )
                )
                FROM user_embeddings
                WHERE emotion IS NOT NULL AND topic IS NOT NULL
                GROUP BY emotion, topic
            )::STRING
        )
    ) as effectiveness_analysis
FROM user_embeddings
LIMIT 1;

-- ============================================
-- NOTES:
-- ============================================
-- 1. Vector embeddings require Cortex EMBED_TEXT function
-- 2. VECTOR_DISTANCE may vary by Snowflake version
-- 3. Replace 'demo_user' with actual user_id in queries
-- 4. These queries showcase the Memory Engine capabilities
-- 5. RAG pipeline: Store → Embed → Retrieve → Personalize
-- ============================================

