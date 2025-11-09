"""
Snowflake Cortex Analysis Service
Uses Cortex LLM functions for advanced longitudinal analysis
Falls back to Gemini Pro if Cortex is not available in region
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


class CortexAnalysisService:
    """
    Service for using Snowflake Cortex for long-term child development analysis
    
    Note: Cortex features may not be available in all regions (e.g., Australia/Azure).
    This service includes fallback logic to use Gemini Pro if Cortex is unavailable.
    """
    
    def __init__(self, snowflake_conn=None):
        """
        Initialize Cortex Analysis Service
        
        Args:
            snowflake_conn: Existing Snowflake connection (optional)
        """
        self.conn = snowflake_conn
        self.cortex_available = False
        self._check_cortex_availability()
    
    def _check_cortex_availability(self):
        """Check if Cortex functions are available in this region"""
        if not self.conn:
            return False
        
        try:
            cursor = self.conn.cursor()
            # Try a simple Cortex function to check availability
            cursor.execute("""
                SELECT SNOWFLAKE.CORTEX.SENTIMENT('test')
            """)
            cursor.fetchone()
            cursor.close()
            self.cortex_available = True
            logger.info("✅ Cortex functions are available in this region")
            return True
        except Exception as e:
            error_msg = str(e).lower()
            if 'cortex' in error_msg or 'not available' in error_msg or 'region' in error_msg:
                self.cortex_available = False
                logger.warning(f"⚠️  Cortex not available in this region: {e}")
                logger.info("   Will use Gemini Pro fallback for analysis")
            else:
                # Other error, might be permissions or syntax
                logger.warning(f"Could not verify Cortex availability: {e}")
                self.cortex_available = False
            return False
    
    def is_available(self) -> bool:
        """Check if Cortex is available for use"""
        return self.cortex_available and self.conn is not None
    
    def analyze_longitudinal_trends(self, child_id: str, days: int = 90) -> Dict:
        """
        Use Cortex to analyze longitudinal development trends across multiple sessions
        
        NOTE: This analyzes data that has already been processed by Gemini Pro for individual sessions.
        Workflow:
        1. Individual sessions → Gemini Pro analyzes each session → Stores in Snowflake
        2. Multiple sessions over time → Cortex analyzes aggregated data → Long-term insights
        
        This generates AI-powered insights about:
        - Overall development trajectory
        - Strengths and growth areas
        - Predictive insights
        - Recommendations
        
        Args:
            child_id: Child identifier
            days: Number of days to analyze (default 90)
            
        Returns:
            Dictionary with analysis results or None if Cortex unavailable
        """
        if not self.is_available():
            logger.info("Cortex not available, skipping Cortex analysis")
            return None
        
        try:
            cursor = self.conn.cursor()
            
            # Get aggregated trend data for analysis
            # Build JSON object manually since Snowflake JSON_OBJECT syntax varies
            # Use ARRAY_AGG with WITHIN GROUP for ordering
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT session_id) as total_sessions,
                    ARRAY_AGG(language_score) WITHIN GROUP (ORDER BY timestamp) as language_trend,
                    ARRAY_AGG(cognitive_score) WITHIN GROUP (ORDER BY timestamp) as cognitive_trend,
                    ARRAY_AGG(emotional_score) WITHIN GROUP (ORDER BY timestamp) as emotional_trend,
                    ARRAY_AGG(social_score) WITHIN GROUP (ORDER BY timestamp) as social_trend,
                    ARRAY_AGG(creativity_score) WITHIN GROUP (ORDER BY timestamp) as creativity_trend,
                    ARRAY_AGG(vocabulary_size) WITHIN GROUP (ORDER BY timestamp) as vocabulary_growth,
                    ARRAY_AGG(sentence_complexity) WITHIN GROUP (ORDER BY timestamp) as complexity_progression,
                    AVG(curiosity_score) as avg_curiosity,
                    AVG(abstract_thinking_score) as avg_abstract_thinking,
                    ARRAY_AGG(DISTINCT top_strength) as top_strengths,
                    ARRAY_AGG(DISTINCT growth_area) as growth_areas
                FROM child_development_sessions
                WHERE child_id = %s
                AND timestamp >= DATEADD(day, -%s, CURRENT_TIMESTAMP())
            """, (child_id, days))
            
            row = cursor.fetchone()
            if not row or row[0] == 0:
                cursor.close()
                return None
            
            # Build trend_data dictionary
            trend_data = {
                'timeframe': f'last_{days}_days',
                'total_sessions': row[0] if row[0] else 0,
                'language_trend': row[1] if row[1] else [],
                'cognitive_trend': row[2] if row[2] else [],
                'emotional_trend': row[3] if row[3] else [],
                'social_trend': row[4] if row[4] else [],
                'creativity_trend': row[5] if row[5] else [],
                'vocabulary_growth': row[6] if row[6] else [],
                'complexity_progression': row[7] if row[7] else [],
                'avg_curiosity': float(row[8]) if row[8] is not None else 0.0,
                'avg_abstract_thinking': float(row[9]) if row[9] is not None else 0.0,
                'top_strengths': row[10] if row[10] else [],
                'growth_areas': row[11] if row[11] else []
            }
            
            # Use Cortex LLM to analyze the trends
            analysis_prompt = f"""
            Analyze this child development data over the past {days} days and provide:
            1. Overall development trajectory (improving, stable, declining)
            2. Top 3 strengths based on the data
            3. Top 2 growth areas that need attention
            4. Predictive insights about future development
            5. Actionable recommendations for parents
            
            Data: {json.dumps(trend_data, indent=2)}
            
            Format your response as JSON with keys: trajectory, strengths, growth_areas, predictions, recommendations
            """
            
            # Use Cortex Complete function for analysis
            cursor.execute("""
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'snowflake-arctic',
                    %s
                )
            """, (analysis_prompt,))
            
            cortex_response = cursor.fetchone()[0]
            cursor.close()
            
            # Parse the response
            try:
                analysis = json.loads(cortex_response)
            except:
                # If not JSON, wrap it
                analysis = {
                    'raw_analysis': cortex_response,
                    'trajectory': 'analyzing',
                    'strengths': [],
                    'growth_areas': [],
                    'predictions': [],
                    'recommendations': []
                }
            
            return {
                'source': 'cortex',
                'analysis': analysis,
                'trend_data': trend_data,
                'analyzed_days': days
            }
            
        except Exception as e:
            logger.error(f"Error in Cortex longitudinal analysis: {e}")
            return None
    
    def generate_insights_query(self, child_id: str, question: str) -> Optional[str]:
        """
        Use Cortex Analyst to answer natural language questions about child development
        
        Example questions:
        - "What are the main trends in language development?"
        - "How has social skills improved over time?"
        - "What activities would help improve cognitive scores?"
        
        Args:
            child_id: Child identifier
            question: Natural language question about the child's development
            
        Returns:
            Answer string or None if Cortex unavailable
        """
        if not self.is_available():
            return None
        
        try:
            cursor = self.conn.cursor()
            
            # Use Cortex Analyst to answer the question
            # Note: This requires Cortex Analyst feature, which has region limitations
            cursor.execute("""
                SELECT SNOWFLAKE.CORTEX.ANALYZE(
                    %s,
                    'SELECT * FROM child_development_sessions WHERE child_id = ?',
                    ARRAY_CONSTRUCT(%s)
                )
            """, (question, child_id))
            
            answer = cursor.fetchone()[0]
            cursor.close()
            
            return answer
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'analyst' in error_msg and 'not available' in error_msg:
                logger.warning("Cortex Analyst not available in this region")
            else:
                logger.error(f"Error in Cortex Analyst query: {e}")
            return None
    
    def detect_patterns(self, child_id: str) -> Dict:
        """
        Use Cortex to detect patterns in child development data
        
        Identifies:
        - Correlation between different development areas
        - Seasonal or temporal patterns
        - Anomalies or outliers
        - Predictive patterns
        
        Args:
            child_id: Child identifier
            
        Returns:
            Dictionary with detected patterns
        """
        if not self.is_available():
            return {}
        
        try:
            cursor = self.conn.cursor()
            
            # Get comprehensive data for pattern detection
            cursor.execute("""
                SELECT 
                    JSON_OBJECT(
                        'sessions': ARRAY_AGG(
                            JSON_OBJECT(
                                'date': DATE(timestamp),
                                'language': language_score,
                                'cognitive': cognitive_score,
                                'emotional': emotional_score,
                                'social': social_score,
                                'creativity': creativity_score,
                                'vocabulary': vocabulary_size,
                                'complexity': sentence_complexity,
                                'curiosity': curiosity_score,
                                'engagement': conversation_turns,
                                'duration': session_duration
                            ) ORDER BY timestamp
                        )
                    )
                FROM child_development_sessions
                WHERE child_id = %s
                ORDER BY timestamp ASC
            """, (child_id,))
            
            pattern_data = cursor.fetchone()[0]
            
            # Use Cortex to detect patterns
            pattern_prompt = f"""
            Analyze this child development data and identify:
            1. Correlations between development areas (e.g., does high language correlate with high cognitive?)
            2. Temporal patterns (e.g., are scores higher on certain days of week?)
            3. Anomalies or outliers that need attention
            4. Predictive patterns (e.g., if X improves, Y typically follows)
            
            Data: {json.dumps(pattern_data, indent=2)}
            
            Format as JSON with keys: correlations, temporal_patterns, anomalies, predictive_patterns
            """
            
            cursor.execute("""
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'snowflake-arctic',
                    %s
                )
            """, (pattern_prompt,))
            
            patterns_response = cursor.fetchone()[0]
            cursor.close()
            
            try:
                patterns = json.loads(patterns_response)
            except:
                patterns = {'raw_response': patterns_response}
            
            return {
                'source': 'cortex',
                'patterns': patterns,
                'data_points': len(pattern_data.get('sessions', []))
            }
            
        except Exception as e:
            logger.error(f"Error in Cortex pattern detection: {e}")
            return {}
    
    def compare_to_benchmarks(self, child_id: str, child_age: int) -> Dict:
        """
        Use Cortex to compare child's development to age-appropriate benchmarks
        
        Args:
            child_id: Child identifier
            child_age: Child's age in years
            
        Returns:
            Dictionary with benchmark comparisons
        """
        if not self.is_available():
            return {}
        
        try:
            cursor = self.conn.cursor()
            
            # Get child's current scores
            cursor.execute("""
                SELECT 
                    AVG(language_score) as avg_language,
                    AVG(cognitive_score) as avg_cognitive,
                    AVG(emotional_score) as avg_emotional,
                    AVG(social_score) as avg_social,
                    AVG(creativity_score) as avg_creativity,
                    AVG(vocabulary_size) as avg_vocabulary,
                    AVG(sentence_complexity) as avg_complexity
                FROM child_development_sessions
                WHERE child_id = %s
                AND timestamp >= DATEADD(day, -30, CURRENT_TIMESTAMP())
            """, (child_id,))
            
            current_scores = cursor.fetchone()
            
            # Age-appropriate benchmarks (these would ideally come from research data)
            benchmarks = {
                3: {'language': 60, 'cognitive': 55, 'vocabulary': 500, 'complexity': 3.5},
                4: {'language': 70, 'cognitive': 65, 'vocabulary': 800, 'complexity': 4.5},
                5: {'language': 80, 'cognitive': 75, 'vocabulary': 1200, 'complexity': 5.5},
                6: {'language': 85, 'cognitive': 80, 'vocabulary': 2000, 'complexity': 6.0}
            }
            
            age_benchmark = benchmarks.get(child_age, benchmarks[5])
            
            comparison_data = {
                'child_age': child_age,
                'current_scores': {
                    'language': float(current_scores[0]) if current_scores[0] else 0,
                    'cognitive': float(current_scores[1]) if current_scores[1] else 0,
                    'emotional': float(current_scores[2]) if current_scores[2] else 0,
                    'social': float(current_scores[3]) if current_scores[3] else 0,
                    'creativity': float(current_scores[4]) if current_scores[4] else 0,
                    'vocabulary': float(current_scores[5]) if current_scores[5] else 0,
                    'complexity': float(current_scores[6]) if current_scores[6] else 0
                },
                'benchmarks': age_benchmark
            }
            
            # Use Cortex to generate comparison insights
            comparison_prompt = f"""
            Compare this {child_age}-year-old child's development scores to age-appropriate benchmarks:
            
            Current Scores: {json.dumps(comparison_data['current_scores'])}
            Age Benchmarks: {json.dumps(age_benchmark)}
            
            Provide:
            1. Areas where child is ahead of benchmarks
            2. Areas where child is on track
            3. Areas where child needs support
            4. Specific recommendations for each area
            
            Format as JSON with keys: ahead_of_benchmark, on_track, needs_support, recommendations
            """
            
            cursor.execute("""
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'snowflake-arctic',
                    %s
                )
            """, (comparison_prompt,))
            
            comparison_response = cursor.fetchone()[0]
            cursor.close()
            
            try:
                comparison_insights = json.loads(comparison_response)
            except:
                comparison_insights = {'raw_response': comparison_response}
            
            return {
                'source': 'cortex',
                'comparison': comparison_insights,
                'data': comparison_data
            }
            
        except Exception as e:
            logger.error(f"Error in Cortex benchmark comparison: {e}")
            return {}
    
    def query_cortex_analyst(self, child_id: str, question: str) -> Dict:
        """
        Use Cortex Analyst to answer natural language questions about child development
        
        This uses Cortex COMPLETE with context from Snowflake data to provide
        intelligent answers about the child's development.
        
        Args:
            child_id: Child identifier
            question: Natural language question about the child
            
        Returns:
            Dictionary with answer and metadata
        """
        if not self.is_available():
            # Fallback to Gemini Pro if Cortex not available
            logger.info("Cortex not available, using Gemini Pro fallback for query")
            return {
                'available': False,
                'message': 'Cortex Analyst not available in this region. Using standard insights.',
                'fallback': 'gemini_pro'
            }
        
        try:
            cursor = self.conn.cursor()
            
            # Get child's development data for context
            cursor.execute("""
                SELECT 
                    child_name,
                    child_age,
                    COUNT(*) as session_count,
                    AVG(language_score) as avg_language,
                    AVG(cognitive_score) as avg_cognitive,
                    AVG(emotional_score) as avg_emotional,
                    AVG(social_score) as avg_social,
                    AVG(creativity_score) as avg_creativity,
                    AVG(vocabulary_size) as avg_vocabulary,
                    MAX(timestamp) as last_session
                FROM child_development_sessions
                WHERE child_id = %s
                GROUP BY child_name, child_age
            """, (child_id,))
            
            child_data = cursor.fetchone()
            
            if not child_data:
                return {
                    'available': False,
                    'message': f'No data found for child {child_id}'
                }
            
            child_name = child_data[0] or 'the child'
            child_age = child_data[1] or 4
            session_count = child_data[2] or 0
            
            # Get recent trends
            cursor.execute("""
                SELECT 
                    AVG(language_score) as recent_language,
                    AVG(cognitive_score) as recent_cognitive,
                    AVG(emotional_score) as recent_emotional,
                    AVG(vocabulary_size) as recent_vocabulary
                FROM child_development_sessions
                WHERE child_id = %s
                AND timestamp >= DATEADD(day, -30, CURRENT_TIMESTAMP())
            """, (child_id,))
            
            recent_data = cursor.fetchone()
            
            # Build context for Cortex
            context_data = {
                'child_name': child_name,
                'child_age': child_age,
                'total_sessions': session_count,
                'average_scores': {
                    'language': float(child_data[3]) if child_data[3] else 0,
                    'cognitive': float(child_data[4]) if child_data[4] else 0,
                    'emotional': float(child_data[5]) if child_data[5] else 0,
                    'social': float(child_data[6]) if child_data[6] else 0,
                    'creativity': float(child_data[7]) if child_data[7] else 0,
                    'vocabulary': float(child_data[8]) if child_data[8] else 0
                },
                'recent_trends': {
                    'language': float(recent_data[0]) if recent_data and recent_data[0] else 0,
                    'cognitive': float(recent_data[1]) if recent_data and recent_data[1] else 0,
                    'emotional': float(recent_data[2]) if recent_data and recent_data[2] else 0,
                    'vocabulary': float(recent_data[3]) if recent_data and recent_data[3] else 0
                }
            }
            
            # Build prompt for Cortex Analyst
            analyst_prompt = f"""You are an expert child development analyst. Answer this question about {child_name}, a {child_age}-year-old child:

Question: {question}

Child Development Data:
- Total Sessions: {session_count}
- Average Scores (0-100):
  * Language: {context_data['average_scores']['language']:.1f}
  * Cognitive: {context_data['average_scores']['cognitive']:.1f}
  * Emotional: {context_data['average_scores']['emotional']:.1f}
  * Social: {context_data['average_scores']['social']:.1f}
  * Creativity: {context_data['average_scores']['creativity']:.1f}
  * Vocabulary Size: {int(context_data['average_scores']['vocabulary'])} words

Recent Trends (Last 30 Days):
- Language: {context_data['recent_trends']['language']:.1f}
- Cognitive: {context_data['recent_trends']['cognitive']:.1f}
- Emotional: {context_data['recent_trends']['emotional']:.1f}
- Vocabulary: {int(context_data['recent_trends']['vocabulary'])} words

Provide a helpful, parent-friendly answer based on this data. Be specific, actionable, and encouraging. If the question asks about trends, compare recent data to overall averages. If asking about recommendations, provide concrete suggestions."""
            
            # Query Cortex COMPLETE
            cursor.execute("""
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'snowflake-arctic',
                    %s
                ) AS answer
            """, (analyst_prompt,))
            
            result = cursor.fetchone()
            answer = result[0] if result else "I couldn't generate an answer. Please try rephrasing your question."
            
            cursor.close()
            
            return {
                'available': True,
                'answer': answer,
                'source': 'Cortex Analyst',
                'child_id': child_id,
                'child_name': child_name,
                'context_used': {
                    'total_sessions': session_count,
                    'data_points': 'development_scores'
                }
            }
            
        except Exception as e:
            logger.error(f"Error in Cortex Analyst query: {e}")
            # Fallback to Gemini Pro
            return {
                'available': False,
                'message': f'Error querying Cortex Analyst: {str(e)}',
                'fallback': 'gemini_pro'
            }

