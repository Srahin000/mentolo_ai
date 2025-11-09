"""
Snowflake Memory Engine - Vector Embeddings & RAG
Creates a personalized knowledge base using Snowflake Cortex embeddings
"Gemini teaches. Snowflake learns."
"""

import os
import logging
from typing import Dict, List, Optional
import json
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

try:
    import snowflake.connector
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False


class SnowflakeMemoryService:
    """
    Memory Engine using Snowflake Cortex Vector Embeddings
    Creates a personalized knowledge base that learns from every interaction
    """
    
    def __init__(self, snowflake_conn=None):
        """
        Initialize Memory Service
        
        Args:
            snowflake_conn: Existing Snowflake connection
        """
        self.conn = snowflake_conn
        self.cortex_available = False
        self.embedding_function = None  # Will be set to EMBED_TEXT_1024, EMBED_TEXT_768, or EMBED_TEXT
        self.embedding_model = None  # Will be set to the model name that works
        self.embedding_dim = 1024  # Default dimension
        self._check_cortex_availability()
        if self.conn:
            self._initialize_memory_schema()
    
    def _check_cortex_availability(self):
        """Check if Cortex embedding functions are available"""
        if not self.conn:
            return False
        
        # Try different embedding function names (newer versions use EMBED_TEXT_768 or EMBED_TEXT_1024)
        embedding_functions = [
            ('EMBED_TEXT_1024', 'snowflake-arctic-embed-m-v1.5'),
            ('EMBED_TEXT_768', 'snowflake-arctic-embed-m-v1.5'),
            ('EMBED_TEXT', 'snowflake-arctic'),
        ]
        
        for func_name, model_name in embedding_functions:
            try:
                cursor = self.conn.cursor()
                # Try Cortex embed function with different names
                cursor.execute(f"""
                    SELECT SNOWFLAKE.CORTEX.{func_name}('{model_name}', 'test')
                """)
                result = cursor.fetchone()
                cursor.close()
                
                # Store which function works
                self.embedding_function = func_name
                self.embedding_model = model_name
                self.embedding_dim = 1024 if '1024' in func_name else (768 if '768' in func_name else 1024)
                
                self.cortex_available = True
                logger.info(f"✅ Cortex embedding functions available: {func_name} with {model_name}")
                return True
            except Exception as e:
                error_msg = str(e).lower()
                if 'cortex' in error_msg or 'embed' in error_msg or 'unknown' in error_msg:
                    # Try next function
                    continue
                else:
                    logger.warning(f"Could not verify Cortex embeddings with {func_name}: {e}")
                    continue
        
        # None of the functions worked
        self.cortex_available = False
        self.embedding_function = None
        self.embedding_model = None
        logger.warning("⚠️  Cortex embeddings not available - tried EMBED_TEXT_1024, EMBED_TEXT_768, EMBED_TEXT")
        return False
    
    def is_available(self) -> bool:
        """Check if memory service is available"""
        return self.cortex_available and self.conn is not None
    
    def _initialize_memory_schema(self):
        """Initialize memory tables for vector embeddings"""
        if not self.conn:
            return
        
        try:
            cursor = self.conn.cursor()
            
            # User embeddings table (vector memory)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_embeddings (
                    embedding_id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    session_id VARCHAR(36),
                    interaction_type VARCHAR(50),
                    question_text TEXT,
                    answer_text TEXT,
                    emotion VARCHAR(50),
                    lesson_tag VARCHAR(100),
                    topic VARCHAR(100),
                    embedding VECTOR(FLOAT, 1024),
                    confidence_score FLOAT,
                    timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                    metadata VARIANT,
                    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
                )
            """)
            
            # Create index for vector similarity search
            try:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_user_embeddings_vector 
                    ON user_embeddings USING VECTOR(embedding)
                """)
            except Exception as e:
                # Vector index might not be supported in all regions
                logger.warning(f"Could not create vector index: {e}")
            
            # User knowledge gaps table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_knowledge_gaps (
                    gap_id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    topic VARCHAR(100),
                    concept VARCHAR(200),
                    first_identified TIMESTAMP_NTZ,
                    last_mentioned TIMESTAMP_NTZ,
                    frequency INTEGER DEFAULT 1,
                    confidence FLOAT,
                    context TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
                )
            """)
            
            # Learning patterns table (cohort analytics)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_patterns (
                    pattern_id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36),
                    pattern_type VARCHAR(50),
                    pattern_data VARIANT,
                    insight TEXT,
                    generated_by VARCHAR(50) DEFAULT 'cortex',
                    timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
                )
            """)
            
            cursor.close()
            self.conn.commit()
            logger.info("✅ Memory schema initialized")
        except Exception as e:
            logger.error(f"Error initializing memory schema: {e}")
            if self.conn:
                self.conn.rollback()
    
    def store_interaction(self, user_id: str, session_id: str, question: str, 
                         answer: str, emotion: str = None, topic: str = None,
                         lesson_tag: str = None, confidence: float = None,
                         metadata: Dict = None) -> bool:
        """
        Store interaction with vector embedding
        
        Creates a memory entry that can be retrieved later for personalization
        """
        if not self.is_available():
            logger.warning("Memory service not available")
            return False
        
        try:
            cursor = self.conn.cursor()
            import uuid
            embedding_id = str(uuid.uuid4())
            
            # Generate embedding using Cortex
            # Combine question and answer for better context
            text_to_embed = f"Question: {question}\nAnswer: {answer}"
            
            # Use the embedding function that was detected as available
            if not self.embedding_function:
                logger.warning("No embedding function available")
                cursor.close()
                return False
            
            cursor.execute(f"""
                SELECT SNOWFLAKE.CORTEX.{self.embedding_function}('{self.embedding_model}', %s) AS embedding
            """, (text_to_embed,))
            
            embedding_result = cursor.fetchone()
            if not embedding_result or not embedding_result[0]:
                logger.warning("Could not generate embedding")
                cursor.close()
                return False
            
            embedding = embedding_result[0]
            
            # Store in user_embeddings table
            cursor.execute("""
                INSERT INTO user_embeddings (
                    embedding_id, user_id, session_id, interaction_type,
                    question_text, answer_text, emotion, lesson_tag, topic,
                    embedding, confidence_score, metadata
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, PARSE_JSON(%s)
                )
            """, (
                embedding_id, user_id, session_id, 'question',
                question, answer, emotion, lesson_tag, topic,
                embedding, confidence or 0.8, json.dumps(metadata or {})
            ))
            
            cursor.close()
            self.conn.commit()
            logger.info(f"✅ Stored interaction memory for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing interaction: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def retrieve_context(self, user_id: str, current_question: str, limit: int = 3) -> List[Dict]:
        """
        Retrieve relevant context using vector similarity (RAG)
        
        Returns past interactions similar to current question for personalization
        """
        if not self.is_available():
            return []
        
        try:
            cursor = self.conn.cursor()
            
            # Generate embedding for current question
            if not self.embedding_function:
                return []
            
            cursor.execute(f"""
                SELECT SNOWFLAKE.CORTEX.{self.embedding_function}('{self.embedding_model}', %s) AS embedding
            """, (current_question,))
            
            query_embedding = cursor.fetchone()[0]
            if not query_embedding:
                return []
            
            # Vector similarity search
            # Note: VECTOR_DISTANCE might need adjustment based on Snowflake version
            cursor.execute("""
                SELECT 
                    question_text,
                    answer_text,
                    topic,
                    lesson_tag,
                    emotion,
                    timestamp,
                    VECTOR_DISTANCE(embedding, %s) as distance
                FROM user_embeddings
                WHERE user_id = %s
                ORDER BY distance ASC
                LIMIT %s
            """, (query_embedding, user_id, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'question': row[0],
                    'answer': row[1],
                    'topic': row[2],
                    'lesson_tag': row[3],
                    'emotion': row[4],
                    'timestamp': str(row[5]) if row[5] else None,
                    'similarity': 1.0 - float(row[6]) if row[6] else 0.0  # Convert distance to similarity
                })
            
            cursor.close()
            logger.info(f"✅ Retrieved {len(results)} relevant memories for user {user_id}")
            return results
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    def identify_knowledge_gap(self, user_id: str, topic: str, concept: str, 
                               context: str = None) -> bool:
        """
        Identify and track knowledge gaps
        
        Uses Cortex to analyze if this is a recurring gap
        """
        if not self.is_available():
            return False
        
        try:
            cursor = self.conn.cursor()
            import uuid
            
            # Check if gap already exists
            cursor.execute("""
                SELECT gap_id, frequency, last_mentioned
                FROM user_knowledge_gaps
                WHERE user_id = %s AND topic = %s AND concept = %s AND resolved = FALSE
            """, (user_id, topic, concept))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update frequency
                cursor.execute("""
                    UPDATE user_knowledge_gaps
                    SET frequency = frequency + 1,
                        last_mentioned = CURRENT_TIMESTAMP(),
                        context = %s
                    WHERE gap_id = %s
                """, (context, existing[0]))
            else:
                # Create new gap
                gap_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO user_knowledge_gaps (
                        gap_id, user_id, topic, concept, context,
                        first_identified, last_mentioned, confidence
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0.7
                    )
                """, (gap_id, user_id, topic, concept, context))
            
            cursor.close()
            self.conn.commit()
            logger.info(f"✅ Identified knowledge gap for user {user_id}: {topic}/{concept}")
            return True
        except Exception as e:
            logger.error(f"Error identifying knowledge gap: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def get_personalized_context(self, user_id: str, current_question: str) -> str:
        """
        Get personalized context string for Gemini
        
        Combines retrieved memories into context for better personalization
        """
        memories = self.retrieve_context(user_id, current_question, limit=3)
        
        if not memories:
            return ""
        
        context_parts = ["Previous interactions:"]
        for i, memory in enumerate(memories, 1):
            context_parts.append(
                f"{i}. Q: {memory['question']}\n   A: {memory['answer']}"
            )
            if memory['topic']:
                context_parts.append(f"   Topic: {memory['topic']}")
        
        return "\n".join(context_parts)
    
    def generate_cohort_insights(self, topic: str = None) -> Dict:
        """
        Generate cohort-level insights using Cortex COMPLETE
        
        Analyzes patterns across all users
        """
        if not self.is_available():
            return {}
        
        try:
            cursor = self.conn.cursor()
            
            # Get aggregated data
            if topic:
                cursor.execute("""
                    SELECT 
                        topic,
                        COUNT(*) as total_interactions,
                        AVG(confidence_score) as avg_confidence,
                        MODE(emotion) as most_common_emotion,
                        COUNT(DISTINCT user_id) as unique_users
                    FROM user_embeddings
                    WHERE topic = %s
                    GROUP BY topic
                """, (topic,))
            else:
                cursor.execute("""
                    SELECT 
                        topic,
                        COUNT(*) as total_interactions,
                        AVG(confidence_score) as avg_confidence,
                        MODE(emotion) as most_common_emotion,
                        COUNT(DISTINCT user_id) as unique_users
                    FROM user_embeddings
                    GROUP BY topic
                    ORDER BY total_interactions DESC
                    LIMIT 10
                """)
            
            cohort_data = []
            for row in cursor.fetchall():
                cohort_data.append({
                    'topic': row[0],
                    'total_interactions': row[1],
                    'avg_confidence': float(row[2]) if row[2] else 0,
                    'most_common_emotion': row[3],
                    'unique_users': row[4]
                })
            
            # Use Cortex to analyze
            analysis_prompt = f"""
            Analyze this learning cohort data and provide insights:
            1. Which topics are most challenging (low confidence)?
            2. Which teaching approaches work best (emotion patterns)?
            3. What recommendations do you have for improving learning outcomes?
            
            Data: {json.dumps(cohort_data, indent=2)}
            """
            
            cursor.execute("""
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'snowflake-arctic',
                    %s
                ) AS analysis
            """, (analysis_prompt,))
            
            analysis = cursor.fetchone()[0]
            cursor.close()
            
            return {
                'cohort_data': cohort_data,
                'analysis': analysis,
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating cohort insights: {e}")
            return {}
    
    def get_learning_summary(self, user_id: str, days: int = 30) -> Dict:
        """
        Generate personalized learning summary using Cortex COMPLETE
        """
        if not self.is_available():
            return {}
        
        try:
            cursor = self.conn.cursor()
            
            # Get user's learning history
            cursor.execute("""
                SELECT 
                    question_text,
                    answer_text,
                    topic,
                    lesson_tag,
                    emotion,
                    confidence_score,
                    timestamp
                FROM user_embeddings
                WHERE user_id = %s
                AND timestamp >= DATEADD(day, -%s, CURRENT_TIMESTAMP())
                ORDER BY timestamp DESC
                LIMIT 50
            """, (user_id, days))
            
            interactions = []
            for row in cursor.fetchall():
                interactions.append({
                    'question': row[0],
                    'answer': row[1],
                    'topic': row[2],
                    'lesson_tag': row[3],
                    'emotion': row[4],
                    'confidence': float(row[5]) if row[5] else 0,
                    'timestamp': str(row[6]) if row[6] else None
                })
            
            # Get knowledge gaps
            cursor.execute("""
                SELECT topic, concept, frequency, context
                FROM user_knowledge_gaps
                WHERE user_id = %s AND resolved = FALSE
                ORDER BY frequency DESC
                LIMIT 5
            """, (user_id,))
            
            gaps = []
            for row in cursor.fetchall():
                gaps.append({
                    'topic': row[0],
                    'concept': row[1],
                    'frequency': row[2],
                    'context': row[3]
                })
            
            # Generate summary with Cortex
            summary_prompt = f"""
            Generate a personalized learning summary for this student:
            
            Recent Interactions ({len(interactions)}):
            {json.dumps(interactions[:10], indent=2)}
            
            Knowledge Gaps:
            {json.dumps(gaps, indent=2)}
            
            Provide:
            1. Progress overview
            2. Strengths identified
            3. Areas needing attention
            4. Recommended next steps
            """
            
            cursor.execute("""
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'snowflake-arctic',
                    %s
                ) AS summary
            """, (summary_prompt,))
            
            summary = cursor.fetchone()[0]
            cursor.close()
            
            return {
                'user_id': user_id,
                'summary': summary,
                'interactions_count': len(interactions),
                'knowledge_gaps': gaps,
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating learning summary: {e}")
            return {}

