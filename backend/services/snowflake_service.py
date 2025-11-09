"""
Snowflake Service - Analytics & AI Insights
Stores user interactions, generates insights, and powers dashboard
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)

try:
    import snowflake.connector
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False
    logger.warning("Snowflake connector not installed. Install with: pip install snowflake-connector-python")


class SnowflakeService:
    def __init__(self):
        self.account = os.getenv('SNOWFLAKE_ACCOUNT')
        self.user = os.getenv('SNOWFLAKE_USER')
        self.password = os.getenv('SNOWFLAKE_PASSWORD')
        self.warehouse = os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH')
        self.database = os.getenv('SNOWFLAKE_DATABASE', 'HOLOMENTOR')
        self.schema = os.getenv('SNOWFLAKE_SCHEMA', 'ANALYTICS')
        self.conn = None
        
        if SNOWFLAKE_AVAILABLE and self.account and self.user and self.password:
            try:
                self.conn = snowflake.connector.connect(
                    user=self.user,
                    password=self.password,
                    account=self.account,
                    warehouse=self.warehouse,
                    database=self.database,
                    schema=self.schema
                )
                self._initialize_schema()
                logger.info("Snowflake service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Snowflake: {e}")
                self.conn = None
        else:
            logger.warning("Snowflake not configured - using local storage fallback")
    
    def is_available(self):
        """Check if Snowflake service is available"""
        return self.conn is not None
    
    def _initialize_schema(self):
        """Initialize Snowflake tables if they don't exist"""
        if not self.conn:
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Try to use existing database (don't create if no permissions)
            database_used = False
            try:
                cursor.execute(f"USE DATABASE {self.database}")
                database_used = True
                logger.info(f"Using database: {self.database}")
            except Exception as e:
                # If database doesn't exist, try to create it
                if "does not exist" in str(e).lower() or "unknown database" in str(e).lower():
                    try:
                        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
                        cursor.execute(f"USE DATABASE {self.database}")
                        database_used = True
                        logger.info(f"Created and using database: {self.database}")
                    except Exception as create_error:
                        logger.warning(f"Cannot create database '{self.database}' (permission issue): {create_error}")
                        # Try to use SNOWFLAKE_LEARNING_DB as fallback
                        try:
                            cursor.execute("USE DATABASE SNOWFLAKE_LEARNING_DB")
                            self.database = "SNOWFLAKE_LEARNING_DB"
                            database_used = True
                            logger.info(f"Using fallback database: SNOWFLAKE_LEARNING_DB")
                        except:
                            logger.warning("No accessible database found. Tables may not be created.")
                else:
                    raise
            
            if not database_used:
                logger.error("Could not access any database. Please create HOLOMENTOR database in Snowflake UI.")
                return
            
            # Try to use existing schema
            try:
                cursor.execute(f"USE SCHEMA {self.schema}")
            except Exception as e:
                # If schema doesn't exist, try to create it
                if "does not exist" in str(e).lower() or "unknown schema" in str(e).lower():
                    try:
                        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {self.schema}")
                        cursor.execute(f"USE SCHEMA {self.schema}")
                    except Exception as create_error:
                        logger.warning(f"Cannot create schema (permission issue): {create_error}")
                        logger.info(f"Using PUBLIC schema instead")
                        cursor.execute("USE SCHEMA PUBLIC")
                        self.schema = "PUBLIC"
                else:
                    raise
            
            # User interactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_interactions (
                    interaction_id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36),
                    session_id VARCHAR(36),
                    timestamp TIMESTAMP_NTZ,
                    interaction_type VARCHAR(50),
                    user_input TEXT,
                    ai_response TEXT,
                    emotion_detected VARCHAR(50),
                    response_time FLOAT,
                    audio_duration FLOAT,
                    model_used VARCHAR(100),
                    metadata VARIANT
                )
            """)
            
            # User profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id VARCHAR(36) PRIMARY KEY,
                    name VARCHAR(255),
                    age INTEGER,
                    created_at TIMESTAMP_NTZ,
                    updated_at TIMESTAMP_NTZ,
                    total_interactions INTEGER DEFAULT 0,
                    learning_goals VARIANT,
                    preferences VARIANT,
                    preferences_json VARIANT,
                    location_json VARIANT
                )
            """)
            
            # Add location_json column if it doesn't exist (for existing tables)
            try:
                cursor.execute("ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS location_json VARIANT")
            except Exception as e:
                # Column might already exist or we don't have ALTER permissions
                logger.debug(f"Could not add location_json column: {e}")
            
            # Learning analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_analytics (
                    analytics_id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36),
                    date DATE,
                    total_sessions INTEGER,
                    avg_response_time FLOAT,
                    topics_covered VARIANT,
                    emotion_trends VARIANT,
                    engagement_score FLOAT,
                    improvement_areas VARIANT,
                    created_at TIMESTAMP_NTZ
                )
            """)
            
            # Child development sessions table (enriched schema)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS child_development_sessions (
                    session_id VARCHAR(36) PRIMARY KEY,
                    child_id VARCHAR(36),
                    child_name VARCHAR(255),
                    child_age INTEGER,
                    timestamp TIMESTAMP_NTZ,
                    transcript TEXT,
                    transcript_length INTEGER,
                    audio_path VARCHAR(500),
                    session_context VARIANT,
                    analysis VARIANT,
                    development_scores VARIANT,
                    vocabulary_analysis VARIANT,
                    cognitive_indicators VARIANT,
                    emotional_intelligence VARIANT,
                    social_skills VARIANT,
                    creativity_imagination VARIANT,
                    speech_clarity VARIANT,
                    -- Core Development Scores (0-100)
                    language_score INTEGER,
                    cognitive_score INTEGER,
                    emotional_score INTEGER,
                    social_score INTEGER,
                    creativity_score INTEGER,
                    -- Language Details
                    vocabulary_size INTEGER,
                    sentence_complexity FLOAT,
                    grammar_accuracy INTEGER,
                    question_frequency INTEGER,
                    -- Engagement Metrics
                    session_duration INTEGER,
                    conversation_turns INTEGER,
                    child_initiated_topics INTEGER,
                    -- AI Metadata
                    daily_insight TEXT,
                    top_strength TEXT,
                    growth_area TEXT,
                    suggested_activity TEXT,
                    -- Emotional Intelligence
                    emotion_words_used INTEGER,
                    empathy_indicators INTEGER,
                    -- Cognitive Patterns
                    reasoning_language_count INTEGER,
                    abstract_thinking_score INTEGER,
                    curiosity_score INTEGER,
                    -- Speech Patterns
                    speech_clarity_score INTEGER,
                    sounds_to_practice VARIANT,
                    created_at TIMESTAMP_NTZ
                )
            """)
            
            # Add new columns if they don't exist (for existing tables)
            new_columns = [
                ("transcript_length", "INTEGER"),
                ("language_score", "INTEGER"),
                ("cognitive_score", "INTEGER"),
                ("emotional_score", "INTEGER"),
                ("social_score", "INTEGER"),
                ("creativity_score", "INTEGER"),
                ("vocabulary_size", "INTEGER"),
                ("sentence_complexity", "FLOAT"),
                ("grammar_accuracy", "INTEGER"),
                ("question_frequency", "INTEGER"),
                ("session_duration", "INTEGER"),
                ("conversation_turns", "INTEGER"),
                ("child_initiated_topics", "INTEGER"),
                ("daily_insight", "TEXT"),
                ("top_strength", "TEXT"),
                ("growth_area", "TEXT"),
                ("suggested_activity", "TEXT"),
                ("emotion_words_used", "INTEGER"),
                ("empathy_indicators", "INTEGER"),
                ("reasoning_language_count", "INTEGER"),
                ("abstract_thinking_score", "INTEGER"),
                ("curiosity_score", "INTEGER"),
                ("speech_clarity_score", "INTEGER"),
                ("sounds_to_practice", "VARIANT")
            ]
            
            for col_name, col_type in new_columns:
                try:
                    cursor.execute(f"ALTER TABLE child_development_sessions ADD COLUMN IF NOT EXISTS {col_name} {col_type}")
                except Exception as e:
                    logger.debug(f"Could not add column {col_name}: {e}")
            
            # Child development trends table (aggregated daily/weekly)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS child_development_trends (
                    trend_id VARCHAR(36) PRIMARY KEY,
                    child_id VARCHAR(36),
                    date DATE,
                    language_score FLOAT,
                    cognitive_score FLOAT,
                    emotional_score FLOAT,
                    social_score FLOAT,
                    creativity_score FLOAT,
                    vocabulary_size INTEGER,
                    sentence_complexity FLOAT,
                    question_frequency INTEGER,
                    curiosity_score FLOAT,
                    strengths_detected VARIANT,
                    growth_areas VARIANT,
                    milestones_progress VARIANT,
                    created_at TIMESTAMP_NTZ
                )
            """)
            
            cursor.close()
            logger.info("Snowflake schema initialized")
        except Exception as e:
            logger.error(f"Error initializing Snowflake schema: {e}")
    
    def log_interaction(self, user_id: str, session_id: str, interaction_data: Dict):
        """Log user interaction to Snowflake"""
        if not self.conn:
            return False
        
        try:
            cursor = self.conn.cursor()
            
            # Convert metadata to VARIANT-compatible format
            metadata = interaction_data.get('metadata', {})
            metadata_json = json.dumps(metadata) if metadata else '{}'
            
            # Use INSERT with SELECT to properly handle VARIANT type
            cursor.execute("""
                INSERT INTO user_interactions (
                    interaction_id, user_id, session_id, timestamp, interaction_type,
                    user_input, ai_response, emotion_detected, response_time,
                    audio_duration, model_used, metadata
                )
                SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, PARSE_JSON(%s)
            """, (
                interaction_data.get('interaction_id'),
                user_id,
                session_id,
                datetime.now(timezone.utc),
                interaction_data.get('type', 'question'),
                interaction_data.get('user_input', ''),
                interaction_data.get('ai_response', ''),
                interaction_data.get('emotion', 'neutral'),
                interaction_data.get('response_time', 0),
                interaction_data.get('audio_duration', 0),
                interaction_data.get('model', 'gemini'),
                metadata_json
            ))
            
            cursor.close()
            logger.info(f"Logged interaction to Snowflake for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error logging to Snowflake: {e}")
            return False
    
    def update_user_profile(self, user_id: str, profile_data: Dict):
        """Update or create user profile in Snowflake"""
        if not self.conn:
            return False
        
        try:
            cursor = self.conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT user_id FROM user_profiles WHERE user_id = %s", (user_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing user
                # Store location in preferences_json if location_json column doesn't exist
                preferences = profile_data.get('preferences', {})
                if profile_data.get('location'):
                    preferences['location'] = profile_data.get('location')
                
                try:
                    # Try with location_json column first
                    # Use TO_VARIANT to convert JSON strings to VARIANT type
                    cursor.execute("""
                        UPDATE user_profiles
                        SET name = %s, age = %s, updated_at = %s,
                            learning_goals = TO_VARIANT(PARSE_JSON(%s)), 
                            preferences_json = TO_VARIANT(PARSE_JSON(%s)), 
                            location_json = TO_VARIANT(PARSE_JSON(%s))
                        WHERE user_id = %s
                    """, (
                        profile_data.get('name'),
                        profile_data.get('age'),
                        datetime.now(timezone.utc),
                        json.dumps(profile_data.get('learning_goals', [])),
                        json.dumps(preferences),
                        json.dumps(profile_data.get('location', {})),
                        user_id
                    ))
                except Exception as e:
                    # Fallback: store location in preferences_json
                    logger.warning(f"Could not update location_json, storing in preferences: {e}")
                    cursor.execute("""
                        UPDATE user_profiles
                        SET name = %s, age = %s, updated_at = %s,
                            learning_goals = TO_VARIANT(PARSE_JSON(%s)), 
                            preferences_json = TO_VARIANT(PARSE_JSON(%s))
                        WHERE user_id = %s
                    """, (
                        profile_data.get('name'),
                        profile_data.get('age'),
                        datetime.now(timezone.utc),
                        json.dumps(profile_data.get('learning_goals', [])),
                        json.dumps(preferences),
                        user_id
                    ))
            else:
                # Create new user
                # Store location in preferences_json if location_json column doesn't exist
                preferences = profile_data.get('preferences', {})
                if profile_data.get('location'):
                    preferences['location'] = profile_data.get('location')
                
                try:
                    # Try with location_json column first
                    # Use sub-SELECT with PARSE_JSON to insert VARIANT values
                    cursor.execute("""
                        INSERT INTO user_profiles (
                            user_id, name, age, created_at, updated_at,
                            learning_goals, preferences_json, location_json
                        )
                        SELECT 
                            %s, %s, %s, %s, %s, 
                            PARSE_JSON(%s), PARSE_JSON(%s), PARSE_JSON(%s)
                    """, (
                        user_id,
                        profile_data.get('name'),
                        profile_data.get('age'),
                        datetime.now(timezone.utc),
                        datetime.now(timezone.utc),
                        json.dumps(profile_data.get('learning_goals', [])),
                        json.dumps(preferences),
                        json.dumps(profile_data.get('location', {}))
                    ))
                except Exception as e:
                    # Fallback: store location in preferences_json
                    logger.warning(f"Could not insert with location_json, storing in preferences: {e}")
                    cursor.execute("""
                        INSERT INTO user_profiles (
                            user_id, name, age, created_at, updated_at,
                            learning_goals, preferences_json
                        )
                        SELECT 
                            %s, %s, %s, %s, %s,
                            PARSE_JSON(%s), PARSE_JSON(%s)
                    """, (
                        user_id,
                        profile_data.get('name'),
                        profile_data.get('age'),
                        datetime.now(timezone.utc),
                        datetime.now(timezone.utc),
                        json.dumps(profile_data.get('learning_goals', [])),
                        json.dumps(preferences)
                    ))
            
            cursor.close()
            self.conn.commit()  # Commit the transaction
            logger.info(f"Updated user profile in Snowflake: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating user profile in Snowflake: {e}")
            self.conn.rollback()  # Rollback on error
            return False
    
    def get_user_insights(self, user_id: str, days: int = 30) -> Dict:
        """Generate AI insights for a user based on their data"""
        if not self.conn:
            return {}
        
        try:
            cursor = self.conn.cursor()
            
            # Get interaction statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_interactions,
                    AVG(response_time) as avg_response_time,
                    AVG(audio_duration) as avg_audio_duration,
                    COUNT(DISTINCT DATE(timestamp)) as active_days,
                    MODE(emotion_detected) as most_common_emotion
                FROM user_interactions
                WHERE user_id = %s
                AND timestamp >= DATEADD(day, -%s, CURRENT_TIMESTAMP())
            """, (user_id, days))
            
            stats = cursor.fetchone()
            
            # Get topics covered (from user_input analysis)
            cursor.execute("""
                SELECT user_input
                FROM user_interactions
                WHERE user_id = %s
                AND timestamp >= DATEADD(day, -%s, CURRENT_TIMESTAMP())
                ORDER BY timestamp DESC
                LIMIT 100
            """, (user_id, days))
            
            topics = [row[0] for row in cursor.fetchall()]
            
            # Get learning progress
            cursor.execute("""
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as interactions,
                    AVG(response_time) as avg_time
                FROM user_interactions
                WHERE user_id = %s
                AND timestamp >= DATEADD(day, -%s, CURRENT_TIMESTAMP())
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            """, (user_id, days))
            
            progress_data = [
                {'date': str(row[0]), 'interactions': row[1], 'avg_time': float(row[2])}
                for row in cursor.fetchall()
            ]
            
            cursor.close()
            
            # Get recent Gemini Pro analysis from child development sessions
            recent_analysis = self._get_recent_gemini_analysis(user_id, days)
            
            return {
                'total_interactions': stats[0] if stats else 0,
                'avg_response_time': float(stats[1]) if stats and stats[1] else 0,
                'avg_audio_duration': float(stats[2]) if stats and stats[2] else 0,
                'active_days': stats[3] if stats else 0,
                'most_common_emotion': stats[4] if stats else 'neutral',
                'topics_covered': topics[:10],  # Last 10 topics
                'progress_timeline': progress_data,
                'engagement_score': self._calculate_engagement(stats, progress_data),
                'insights': self._generate_ai_insights(stats, progress_data, topics, recent_analysis),
                'recent_chat_analysis': recent_analysis  # Gemini Pro analysis from recent sessions
            }
        except Exception as e:
            logger.error(f"Error getting user insights: {e}")
            return {}
    
    def _calculate_engagement(self, stats, progress_data) -> float:
        """Calculate engagement score (0-1)"""
        if not stats or not progress_data:
            return 0.5
        
        total_interactions = stats[0]
        active_days = stats[3]
        
        # Engagement based on frequency and consistency
        frequency_score = min(1.0, total_interactions / (active_days * 5))  # 5 interactions/day = max
        consistency_score = min(1.0, active_days / 30)  # 30 days active = max
        
        return (frequency_score + consistency_score) / 2
    
    def _get_recent_gemini_analysis(self, user_id: str, days: int = 30) -> Dict:
        """Get recent Gemini Pro analysis from child development sessions"""
        if not self.conn:
            return {}
        
        try:
            cursor = self.conn.cursor()
            
            # Get most recent sessions with Gemini Pro analysis
            cursor.execute("""
                SELECT 
                    session_id,
                    child_name,
                    timestamp,
                    analysis,
                    session_context
                FROM child_development_sessions
                WHERE child_id = %s
                AND timestamp >= DATEADD(day, -%s, CURRENT_TIMESTAMP())
                ORDER BY timestamp DESC
                LIMIT 5
            """, (user_id, days))
            
            sessions = []
            all_insights = []
            all_activities = []
            all_growth_opportunities = []
            all_strengths = []
            
            for row in cursor.fetchall():
                import json
                analysis_data = json.loads(row[3]) if isinstance(row[3], str) else row[3]
                context_data = json.loads(row[4]) if isinstance(row[4], str) else row[4]
                
                if analysis_data:
                    sessions.append({
                        'session_id': row[0],
                        'child_name': row[1],
                        'timestamp': row[2].isoformat() if hasattr(row[2], 'isoformat') else str(row[2]),
                        'daily_insight': analysis_data.get('daily_insight', ''),
                        'strengths': analysis_data.get('strengths', []),
                        'growth_opportunities': analysis_data.get('growth_opportunities', []),
                        'personalized_activities': analysis_data.get('personalized_activities', [])
                    })
                    
                    # Aggregate insights from Gemini Pro
                    if analysis_data.get('daily_insight'):
                        all_insights.append(analysis_data.get('daily_insight'))
                    if analysis_data.get('personalized_activities'):
                        all_activities.extend(analysis_data.get('personalized_activities', []))
                    if analysis_data.get('growth_opportunities'):
                        all_growth_opportunities.extend(analysis_data.get('growth_opportunities', []))
                    if analysis_data.get('strengths'):
                        all_strengths.extend(analysis_data.get('strengths', []))
            
            cursor.close()
            
            return {
                'recent_sessions': sessions,
                'aggregated_insights': all_insights[:5],  # Top 5 recent insights from Gemini Pro
                'recommended_activities': all_activities[:5],  # Top 5 activities from Gemini Pro
                'growth_areas': all_growth_opportunities[:3],  # Top 3 growth areas
                'strengths': all_strengths[:3],  # Top 3 strengths
                'total_sessions_analyzed': len(sessions)
            }
        except Exception as e:
            logger.error(f"Error getting Gemini Pro analysis: {e}")
            return {}
    
    def _generate_ai_insights(self, stats, progress_data, topics, recent_analysis: Dict = None) -> List[str]:
        """Generate AI-powered insights using Gemini Pro analysis from recent chats"""
        insights = []
        
        # PRIORITY: Use Gemini Pro insights from recent sessions
        if recent_analysis and recent_analysis.get('aggregated_insights'):
            # Use Gemini Pro's daily insights (these are from Gemini Pro analysis)
            insights.extend(recent_analysis.get('aggregated_insights', [])[:3])
        
        # Fallback to rule-based insights if no Gemini Pro analysis available
        if not insights and stats:
            total = stats[0]
            avg_time = float(stats[1]) if stats[1] else 0
            emotion = stats[4] if stats[4] else 'neutral'
            
            if total > 50:
                insights.append(f"🌟 Great progress! You've had {total} learning interactions.")
            elif total > 20:
                insights.append(f"📈 You're building a good learning habit with {total} interactions.")
            else:
                insights.append(f"💪 Keep going! You've started with {total} interactions.")
            
            if avg_time < 1.0:
                insights.append("⚡ Fast responses show you're asking great questions!")
            elif avg_time > 2.0:
                insights.append("🤔 Complex questions take more time - that's great for deep learning!")
            
            if emotion == 'excited':
                insights.append("😊 Your enthusiasm is showing! Keep that energy!")
            elif emotion == 'confused':
                insights.append("💡 It's okay to be confused - that's when real learning happens!")
        
        # Add growth opportunities from Gemini Pro
        if recent_analysis and recent_analysis.get('growth_areas'):
            for growth in recent_analysis.get('growth_areas', [])[:2]:
                if isinstance(growth, dict) and growth.get('next_step'):
                    insights.append(f"🎯 {growth.get('area', 'Skill')}: {growth.get('next_step', '')}")
        
        # Progress insights (keep these for engagement tracking)
        if progress_data and len(progress_data) > 7:
            recent_avg = sum(p['interactions'] for p in progress_data[:7]) / 7
            older_avg = sum(p['interactions'] for p in progress_data[7:14]) / 7 if len(progress_data) > 14 else recent_avg
            
            if recent_avg > older_avg * 1.2:
                insights.append("📊 Your learning activity is increasing - excellent momentum!")
        
        return insights[:5]  # Return top 5 insights
    
    def get_dashboard_data(self, user_id: str) -> Dict:
        """Get comprehensive dashboard data with Gemini Pro insights"""
        insights = self.get_user_insights(user_id)
        
        return {
            'user_id': user_id,
            'summary': {
                'total_interactions': insights.get('total_interactions', 0),
                'active_days': insights.get('active_days', 0),
                'engagement_score': insights.get('engagement_score', 0.5),
                'most_common_emotion': insights.get('most_common_emotion', 'neutral')
            },
            'performance': {
                'avg_response_time': insights.get('avg_response_time', 0),
                'avg_audio_duration': insights.get('avg_audio_duration', 0),
                'progress_timeline': insights.get('progress_timeline', [])
            },
            'topics': insights.get('topics_covered', []),
            'ai_insights': insights.get('insights', []),  # Now uses Gemini Pro insights
            'recommendations': self._generate_recommendations(insights),
            'recent_chat_analysis': insights.get('recent_chat_analysis', {})  # Gemini Pro analysis from recent sessions
        }
    
    def _generate_recommendations(self, insights: Dict) -> List[str]:
        """Generate personalized recommendations from Gemini Pro analysis"""
        recommendations = []
        
        # PRIORITY: Use Gemini Pro's recommended activities first
        recent_analysis = insights.get('recent_chat_analysis', {})
        if recent_analysis and recent_analysis.get('recommended_activities'):
            for activity in recent_analysis.get('recommended_activities', [])[:3]:
                if isinstance(activity, dict):
                    title = activity.get('title', '')
                    duration = activity.get('duration', '10 minutes')
                    if title:
                        recommendations.append(f"📚 {title} ({duration})")
        
        # Fallback to rule-based recommendations if no Gemini Pro activities
        if not recommendations:
            engagement = insights.get('engagement_score', 0.5)
            total = insights.get('total_interactions', 0)
            emotion = insights.get('most_common_emotion', 'neutral')
            
            if engagement < 0.3:
                recommendations.append("Try setting a daily learning goal to build consistency")
            
            if total < 10:
                recommendations.append("Explore different topics to discover what interests you most")
            
            if emotion == 'frustrated':
                recommendations.append("Take breaks between sessions - learning should be enjoyable!")
            
            if engagement > 0.7:
                recommendations.append("You're doing great! Consider challenging yourself with more complex topics")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def save_child_development_session(self, session_data: Dict) -> bool:
        """
        Save child development session analysis to Snowflake
        
        Args:
            session_data: Dict containing session_id, child_id, transcript, analysis, etc.
        
        Returns:
            bool: True if saved successfully
        """
        if not self.conn:
            return False
        
        try:
            cursor = self.conn.cursor()
            
            analysis = session_data.get('analysis', {})
            dev_snapshot = analysis.get('development_snapshot', {})
            
            # Extract enriched fields from analysis
            transcript = session_data.get('transcript', '')
            transcript_length = len(transcript)
            
            # Core scores
            language_score = dev_snapshot.get('language', {}).get('score', 0)
            cognitive_score = dev_snapshot.get('cognitive', {}).get('score', 0)
            emotional_score = dev_snapshot.get('emotional', {}).get('score', 0)
            social_score = dev_snapshot.get('social', {}).get('score', 0)
            creativity_score = dev_snapshot.get('creativity', {}).get('score', 0)
            
            # Convert complex objects to JSON for VARIANT
            analysis_json = json.dumps(analysis)
            dev_scores_json = json.dumps({
                'language': language_score,
                'cognitive': cognitive_score,
                'emotional': emotional_score,
                'social': social_score,
                'creativity': creativity_score
            })
            
            vocab_analysis = analysis.get('vocabulary_analysis', {})
            cognitive_indicators = analysis.get('cognitive_indicators', {})
            emotional_intel = analysis.get('emotional_intelligence', {})
            social_skills = analysis.get('social_skills', {})
            creativity = analysis.get('creativity_imagination', {})
            speech = analysis.get('speech_clarity', {})
            
            # Language details
            vocabulary_size = vocab_analysis.get('vocabulary_size_estimate', vocab_analysis.get('vocabulary_size', 0))
            sentence_complexity = vocab_analysis.get('sentence_complexity', 0.0)
            grammar_accuracy = vocab_analysis.get('grammar_accuracy', 0)
            question_frequency = vocab_analysis.get('question_frequency', cognitive_indicators.get('curiosity_score', 0) // 10)
            
            # Engagement metrics
            session_context = session_data.get('session_context', {})
            session_duration = session_context.get('duration_minutes', 3) * 60  # Convert to seconds
            conversation_turns = vocab_analysis.get('conversation_turns', 0)
            child_name = session_data.get('child_name', 'Child')
            child_initiated_topics = len([t for t in transcript.split('\n') if child_name in t or 'Child:' in t]) // 2
            
            # AI metadata
            daily_insight = analysis.get('daily_insight', '')
            strengths_list = analysis.get('strengths', [])
            top_strength = strengths_list[0].get('title', '') if strengths_list else ''
            growth_opps = analysis.get('growth_opportunities', [])
            growth_area = growth_opps[0].get('area', '') if growth_opps else ''
            activities = analysis.get('personalized_activities', [])
            suggested_activity = activities[0].get('title', '') if activities else ''
            
            # Emotional intelligence
            emotion_words_used = len(emotional_intel.get('emotion_words_used', []))
            empathy_indicators = len(emotional_intel.get('empathy_indicators', []))
            
            # Cognitive patterns
            reasoning_language_count = len(cognitive_indicators.get('reasoning_language', []))
            abstract_thinking_score = cognitive_indicators.get('abstract_thinking_score', 0)
            curiosity_score = cognitive_indicators.get('curiosity_score', 0)
            
            # Speech patterns
            speech_clarity_score = speech.get('intelligibility', speech.get('speech_clarity_score', 0))
            sounds_to_practice = speech.get('sounds_to_practice', [])
            
            cursor.execute("""
                INSERT INTO child_development_sessions (
                    session_id, child_id, child_name, child_age, timestamp,
                    transcript, transcript_length, audio_path, session_context, analysis,
                    development_scores, vocabulary_analysis, cognitive_indicators,
                    emotional_intelligence, social_skills, creativity_imagination,
                    speech_clarity,
                    -- Enriched fields
                    language_score, cognitive_score, emotional_score, social_score, creativity_score,
                    vocabulary_size, sentence_complexity, grammar_accuracy, question_frequency,
                    session_duration, conversation_turns, child_initiated_topics,
                    daily_insight, top_strength, growth_area, suggested_activity,
                    emotion_words_used, empathy_indicators,
                    reasoning_language_count, abstract_thinking_score, curiosity_score,
                    speech_clarity_score, sounds_to_practice,
                    created_at
                )
                SELECT 
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, PARSE_JSON(%s), PARSE_JSON(%s),
                    PARSE_JSON(%s), PARSE_JSON(%s), PARSE_JSON(%s),
                    PARSE_JSON(%s), PARSE_JSON(%s), PARSE_JSON(%s),
                    PARSE_JSON(%s),
                    -- Enriched fields
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s,
                    %s, %s, %s,
                    %s, PARSE_JSON(%s),
                    %s
            """, (
                session_data.get('session_id'),
                session_data.get('user_id') or session_data.get('child_id'),
                session_data.get('child_name'),
                session_data.get('child_age'),
                datetime.now(timezone.utc),
                transcript,
                transcript_length,
                session_data.get('audio_path', ''),
                json.dumps(session_context),
                analysis_json,
                dev_scores_json,
                json.dumps(vocab_analysis),
                json.dumps(cognitive_indicators),
                json.dumps(emotional_intel),
                json.dumps(social_skills),
                json.dumps(creativity),
                json.dumps(speech),
                # Enriched fields
                language_score,
                cognitive_score,
                emotional_score,
                social_score,
                creativity_score,
                vocabulary_size,
                sentence_complexity,
                grammar_accuracy,
                question_frequency,
                session_duration,
                conversation_turns,
                child_initiated_topics,
                daily_insight,
                top_strength,
                growth_area,
                suggested_activity,
                emotion_words_used,
                empathy_indicators,
                reasoning_language_count,
                abstract_thinking_score,
                curiosity_score,
                speech_clarity_score,
                json.dumps(sounds_to_practice),
                datetime.now(timezone.utc)
            ))
            
            # Also update trends table for daily aggregation
            self._update_development_trends(
                child_id=session_data.get('user_id') or session_data.get('child_id'),
                analysis=analysis
            )
            
            cursor.close()
            logger.info(f"Saved child development session to Snowflake: {session_data.get('session_id')}")
            return True
        except Exception as e:
            logger.error(f"Error saving child development session to Snowflake: {e}")
            return False
    
    def _update_development_trends(self, child_id: str, analysis: Dict):
        """Update daily development trends"""
        if not self.conn:
            return
        
        try:
            cursor = self.conn.cursor()
            
            dev_snapshot = analysis.get('development_snapshot', {})
            vocab = analysis.get('vocabulary_analysis', {})
            cognitive = analysis.get('cognitive_indicators', {})
            
            today = datetime.now(timezone.utc).date()
            trend_id = f"{child_id}_{today}"
            
            # Check if trend exists for today
            cursor.execute("""
                SELECT trend_id FROM child_development_trends
                WHERE child_id = %s AND date = %s
            """, (child_id, today))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing trend (average with new data)
                cursor.execute("""
                    UPDATE child_development_trends
                    SET 
                        language_score = (language_score + %s) / 2,
                        cognitive_score = (cognitive_score + %s) / 2,
                        emotional_score = (emotional_score + %s) / 2,
                        social_score = (social_score + %s) / 2,
                        creativity_score = (creativity_score + %s) / 2,
                        vocabulary_size = GREATEST(vocabulary_size, %s),
                        sentence_complexity = (sentence_complexity + %s) / 2,
                        question_frequency = question_frequency + %s,
                        curiosity_score = (curiosity_score + %s) / 2,
                        strengths_detected = PARSE_JSON(%s),
                        growth_areas = PARSE_JSON(%s),
                        milestones_progress = PARSE_JSON(%s),
                        created_at = %s
                    WHERE child_id = %s AND date = %s
                """, (
                    dev_snapshot.get('language', {}).get('score', 0),
                    dev_snapshot.get('cognitive', {}).get('score', 0),
                    dev_snapshot.get('emotional', {}).get('score', 0),
                    dev_snapshot.get('social', {}).get('score', 0),
                    dev_snapshot.get('creativity', {}).get('score', 0),
                    vocab.get('vocabulary_size_estimate', 0),
                    vocab.get('sentence_complexity', 0),
                    vocab.get('question_frequency', 0),
                    cognitive.get('curiosity_score', 0),
                    json.dumps([s.get('title', '') for s in analysis.get('strengths', [])]),
                    json.dumps([g.get('area', '') for g in analysis.get('growth_opportunities', [])]),
                    json.dumps(analysis.get('milestone_progress', {})),
                    datetime.now(timezone.utc),
                    child_id,
                    today
                ))
            else:
                # Create new trend
                cursor.execute("""
                    INSERT INTO child_development_trends (
                        trend_id, child_id, date,
                        language_score, cognitive_score, emotional_score,
                        social_score, creativity_score,
                        vocabulary_size, sentence_complexity, question_frequency,
                        curiosity_score, strengths_detected, growth_areas,
                        milestones_progress, created_at
                    )
                    SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                           PARSE_JSON(%s), PARSE_JSON(%s), PARSE_JSON(%s), %s
                """, (
                    trend_id, child_id, today,
                    dev_snapshot.get('language', {}).get('score', 0),
                    dev_snapshot.get('cognitive', {}).get('score', 0),
                    dev_snapshot.get('emotional', {}).get('score', 0),
                    dev_snapshot.get('social', {}).get('score', 0),
                    dev_snapshot.get('creativity', {}).get('score', 0),
                    vocab.get('vocabulary_size_estimate', 0),
                    vocab.get('sentence_complexity', 0),
                    vocab.get('question_frequency', 0),
                    cognitive.get('curiosity_score', 0),
                    json.dumps([s.get('title', '') for s in analysis.get('strengths', [])]),
                    json.dumps([g.get('area', '') for g in analysis.get('growth_opportunities', [])]),
                    json.dumps(analysis.get('milestone_progress', {})),
                    datetime.now(timezone.utc)
                ))
            
            cursor.close()
        except Exception as e:
            logger.error(f"Error updating development trends: {e}")
    
    def get_child_development_insights(self, child_id: str, days: int = 30) -> Dict:
        """
        Generate comprehensive child development insights from Snowflake data
        
        Returns:
            Dict with trends, strengths, growth areas, and AI-generated insights
        """
        if not self.conn:
            return {}
        
        try:
            cursor = self.conn.cursor()
            
            # Get development trends over time
            cursor.execute("""
                SELECT 
                    date,
                    language_score,
                    cognitive_score,
                    emotional_score,
                    social_score,
                    creativity_score,
                    vocabulary_size,
                    sentence_complexity,
                    question_frequency,
                    curiosity_score
                FROM child_development_trends
                WHERE child_id = %s
                AND date >= DATEADD(day, -%s, CURRENT_DATE())
                ORDER BY date ASC
            """, (child_id, days))
            
            trends_data = []
            for row in cursor.fetchall():
                trends_data.append({
                    'date': str(row[0]),
                    'language': float(row[1]) if row[1] else 0,
                    'cognitive': float(row[2]) if row[2] else 0,
                    'emotional': float(row[3]) if row[3] else 0,
                    'social': float(row[4]) if row[4] else 0,
                    'creativity': float(row[5]) if row[5] else 0,
                    'vocabulary_size': int(row[6]) if row[6] else 0,
                    'sentence_complexity': float(row[7]) if row[7] else 0,
                    'question_frequency': int(row[8]) if row[8] else 0,
                    'curiosity_score': float(row[9]) if row[9] else 0
                })
            
            # Get recent sessions for detailed analysis
            cursor.execute("""
                SELECT 
                    session_id,
                    timestamp,
                    development_scores,
                    vocabulary_analysis,
                    strengths_detected,
                    growth_areas
                FROM child_development_sessions
                WHERE child_id = %s
                AND timestamp >= DATEADD(day, -%s, CURRENT_TIMESTAMP())
                ORDER BY timestamp DESC
                LIMIT 10
            """, (child_id, days))
            
            recent_sessions = []
            all_strengths = []
            all_growth_areas = []
            
            for row in cursor.fetchall():
                session_data = {
                    'session_id': row[0],
                    'timestamp': str(row[1]),
                    'scores': json.loads(row[2]) if row[2] else {},
                    'vocabulary': json.loads(row[3]) if row[3] else {},
                    'strengths': json.loads(row[4]) if row[4] else [],
                    'growth_areas': json.loads(row[5]) if row[5] else []
                }
                recent_sessions.append(session_data)
                all_strengths.extend(session_data.get('strengths', []))
                all_growth_areas.extend(session_data.get('growth_areas', []))
            
            # Calculate aggregate statistics
            if trends_data:
                latest = trends_data[-1]
                earliest = trends_data[0] if len(trends_data) > 1 else latest
                
                vocabulary_growth = latest.get('vocabulary_size', 0) - earliest.get('vocabulary_size', 0)
                complexity_change = latest.get('sentence_complexity', 0) - earliest.get('sentence_complexity', 0)
                avg_scores = {
                    'language': sum(t.get('language', 0) for t in trends_data) / len(trends_data),
                    'cognitive': sum(t.get('cognitive', 0) for t in trends_data) / len(trends_data),
                    'emotional': sum(t.get('emotional', 0) for t in trends_data) / len(trends_data),
                    'social': sum(t.get('social', 0) for t in trends_data) / len(trends_data),
                    'creativity': sum(t.get('creativity', 0) for t in trends_data) / len(trends_data)
                }
            else:
                vocabulary_growth = 0
                complexity_change = 0
                avg_scores = {}
            
            # Generate AI insights
            insights = self._generate_child_development_insights(
                trends_data, recent_sessions, vocabulary_growth, complexity_change, avg_scores
            )
            
            cursor.close()
            
            return {
                'child_id': child_id,
                'trends': trends_data,
                'recent_sessions': recent_sessions,
                'statistics': {
                    'total_sessions': len(recent_sessions),
                    'vocabulary_growth': vocabulary_growth,
                    'complexity_change': complexity_change,
                    'average_scores': avg_scores,
                    'most_common_strengths': self._get_most_common(all_strengths, 5),
                    'most_common_growth_areas': self._get_most_common(all_growth_areas, 5)
                },
                'insights': insights,
                'recommendations': self._generate_child_recommendations(trends_data, avg_scores)
            }
        except Exception as e:
            logger.error(f"Error getting child development insights: {e}")
            return {}
    
    def _generate_child_development_insights(self, trends: List[Dict], sessions: List[Dict],
                                            vocab_growth: int, complexity_change: float,
                                            avg_scores: Dict) -> List[str]:
        """Generate AI-powered insights for child development"""
        insights = []
        
        if not trends:
            return ["Start tracking sessions to see personalized insights!"]
        
        # Vocabulary growth insight
        if vocab_growth > 20:
            insights.append(f"🌟 Amazing vocabulary growth! Your child has learned {vocab_growth} new words!")
        elif vocab_growth > 10:
            insights.append(f"📚 Great progress! Vocabulary is expanding with {vocab_growth} new words.")
        elif vocab_growth > 0:
            insights.append(f"💪 Steady vocabulary growth of {vocab_growth} words - keep it up!")
        
        # Complexity insight
        if complexity_change > 1.0:
            insights.append(f"🎯 Sentence complexity is improving! Your child is using more sophisticated language.")
        elif complexity_change < -0.5:
            insights.append(f"💡 Sentence complexity varies - this is normal as children experiment with language.")
        
        # Score-based insights
        if avg_scores:
            highest_area = max(avg_scores.items(), key=lambda x: x[1])
            lowest_area = min(avg_scores.items(), key=lambda x: x[1])
            
            if highest_area[1] > 80:
                insights.append(f"🏆 {highest_area[0].title()} skills are exceptional! Your child excels in this area.")
            
            if lowest_area[1] < 60 and highest_area[1] > 70:
                insights.append(f"📈 Focus on {lowest_area[0]} development - there's great potential for growth!")
        
        # Trend insights
        if len(trends) > 7:
            recent_avg = sum(t.get('language', 0) for t in trends[-7:]) / 7
            older_avg = sum(t.get('language', 0) for t in trends[:7]) / 7 if len(trends) > 14 else recent_avg
            
            if recent_avg > older_avg * 1.1:
                insights.append("📊 Language development is accelerating! Your child is making great progress.")
        
        # Session frequency insight
        if len(sessions) >= 10:
            insights.append(f"🎉 Consistency is key! {len(sessions)} sessions tracked - excellent engagement!")
        elif len(sessions) >= 5:
            insights.append(f"💪 Building a great learning habit with {len(sessions)} sessions!")
        
        return insights if insights else ["Keep engaging with your child to see more insights!"]
    
    def _generate_child_recommendations(self, trends: List[Dict], avg_scores: Dict) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if not trends or not avg_scores:
            return ["Start tracking sessions to get personalized recommendations"]
        
        # Language recommendations
        if avg_scores.get('language', 0) < 70:
            recommendations.append("Try reading together daily - it's the best way to build vocabulary!")
        
        # Cognitive recommendations
        if avg_scores.get('cognitive', 0) < 70:
            recommendations.append("Ask 'why' and 'how' questions to encourage critical thinking")
        
        # Social recommendations
        if avg_scores.get('social', 0) < 70:
            recommendations.append("Practice turn-taking in conversations and games")
        
        # Creativity recommendations
        if avg_scores.get('creativity', 0) < 70:
            recommendations.append("Encourage pretend play and imaginative storytelling")
        
        # General recommendations
        if len(trends) < 5:
            recommendations.append("Track more sessions to see detailed progress patterns")
        
        return recommendations if recommendations else ["Keep up the great work!"]
    
    def _get_most_common(self, items: List, limit: int = 5) -> List[str]:
        """Get most common items from list"""
        from collections import Counter
        if not items:
            return []
        counter = Counter(items)
        return [item for item, count in counter.most_common(limit)]
    
    def get_child_development_sessions(self, child_id: str, limit: int = 50) -> List[Dict]:
        """
        Get child development sessions with all enriched columns from Snowflake
        
        Args:
            child_id: Child identifier
            limit: Maximum number of sessions to retrieve
            
        Returns:
            List of session dictionaries with all enriched columns
        """
        if not self.conn:
            return []
        
        try:
            cursor = self.conn.cursor()
            
            # Get all enriched columns from child_development_sessions
            cursor.execute("""
                SELECT 
                    session_id,
                    child_id,
                    child_name,
                    child_age,
                    timestamp,
                    transcript,
                    transcript_length,
                    audio_path,
                    session_context,
                    analysis,
                    development_scores,
                    vocabulary_analysis,
                    cognitive_indicators,
                    emotional_intelligence,
                    social_skills,
                    creativity_imagination,
                    speech_clarity,
                    -- Core Development Scores
                    language_score,
                    cognitive_score,
                    emotional_score,
                    social_score,
                    creativity_score,
                    -- Language Details
                    vocabulary_size,
                    sentence_complexity,
                    grammar_accuracy,
                    question_frequency,
                    -- Engagement Metrics
                    session_duration,
                    conversation_turns,
                    child_initiated_topics,
                    -- AI Metadata
                    daily_insight,
                    top_strength,
                    growth_area,
                    suggested_activity,
                    -- Emotional Intelligence
                    emotion_words_used,
                    empathy_indicators,
                    -- Cognitive Patterns
                    reasoning_language_count,
                    abstract_thinking_score,
                    curiosity_score,
                    -- Speech Patterns
                    speech_clarity_score,
                    sounds_to_practice
                FROM child_development_sessions
                WHERE child_id = %s
                ORDER BY timestamp DESC
                LIMIT %s
            """, (child_id, limit))
            
            sessions = []
            for row in cursor.fetchall():
                import json
                
                # Safety check: ensure we have enough columns
                if len(row) < 40:
                    logger.warning(f"Row has only {len(row)} columns, expected at least 40. Skipping session.")
                    continue
                
                # Parse VARIANT columns
                session_context = json.loads(row[8]) if row[8] and isinstance(row[8], str) else (row[8] if row[8] else {})
                analysis = json.loads(row[9]) if row[9] and isinstance(row[9], str) else (row[9] if row[9] else {})
                development_scores = json.loads(row[10]) if row[10] and isinstance(row[10], str) else (row[10] if row[10] else {})
                vocabulary_analysis = json.loads(row[11]) if row[11] and isinstance(row[11], str) else (row[11] if row[11] else {})
                cognitive_indicators = json.loads(row[12]) if row[12] and isinstance(row[12], str) else (row[12] if row[12] else {})
                emotional_intelligence = json.loads(row[13]) if row[13] and isinstance(row[13], str) else (row[13] if row[13] else {})
                social_skills = json.loads(row[14]) if row[14] and isinstance(row[14], str) else (row[14] if row[14] else {})
                creativity_imagination = json.loads(row[15]) if row[15] and isinstance(row[15], str) else (row[15] if row[15] else {})
                speech_clarity = json.loads(row[16]) if row[16] and isinstance(row[16], str) else (row[16] if row[16] else {})
                # sounds_to_practice is at index 39 (last column in SELECT)
                sounds_to_practice = json.loads(row[39]) if len(row) > 39 and row[39] and isinstance(row[39], str) else (row[39] if len(row) > 39 and row[39] else [])
                
                session = {
                    'session_id': row[0],
                    'user_id': row[1],  # child_id
                    'child_name': row[2],
                    'child_age': row[3],
                    'timestamp': row[4].isoformat() if hasattr(row[4], 'isoformat') else str(row[4]),
                    'transcript': row[5] or '',
                    'transcript_length': row[6] or 0,
                    'audio_path': row[7] or '',
                    'session_context': session_context,
                    'analysis': analysis,
                    'development_scores': development_scores,
                    'vocabulary_analysis': vocabulary_analysis,
                    'cognitive_indicators': cognitive_indicators,
                    'emotional_intelligence': emotional_intelligence,
                    'social_skills': social_skills,
                    'creativity_imagination': creativity_imagination,
                    'speech_clarity': speech_clarity,
                    # Core Development Scores
                    'language_score': row[17] or 0,
                    'cognitive_score': row[18] or 0,
                    'emotional_score': row[19] or 0,
                    'social_score': row[20] or 0,
                    'creativity_score': row[21] or 0,
                    # Language Details
                    'vocabulary_size': row[22] or 0,
                    'sentence_complexity': float(row[23]) if row[23] else 0.0,
                    'grammar_accuracy': row[24] or 0,
                    'question_frequency': row[25] or 0,
                    # Engagement Metrics
                    'session_duration': row[26] or 0,  # in seconds
                    'conversation_turns': row[27] or 0,
                    'child_initiated_topics': row[28] or 0,
                    # AI Metadata
                    'daily_insight': row[29] or '',
                    'top_strength': row[30] or '',
                    'growth_area': row[31] or '',
                    'suggested_activity': row[32] or '',
                    # Emotional Intelligence
                    'emotion_words_used': row[33] or 0,
                    'empathy_indicators': row[34] or 0,
                    # Cognitive Patterns
                    'reasoning_language_count': row[35] or 0,
                    'abstract_thinking_score': row[36] or 0,
                    'curiosity_score': row[37] or 0,
                    # Speech Patterns
                    'speech_clarity_score': row[38] or 0,
                    'sounds_to_practice': sounds_to_practice
                }
                
                sessions.append(session)
            
            cursor.close()
            logger.info(f"Retrieved {len(sessions)} sessions with enriched data for child {child_id}")
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting child development sessions: {e}")
            return []
    
    def get_child_longitudinal_analysis(self, child_id: str) -> Dict:
        """
        Get longitudinal analysis for child development dashboard
        Includes vocabulary growth, complexity progression, consistency metrics
        """
        if not self.conn:
            return {}
        
        try:
            cursor = self.conn.cursor()
            
            # Get all trends
            cursor.execute("""
                SELECT 
                    date,
                    vocabulary_size,
                    sentence_complexity,
                    language_score,
                    cognitive_score,
                    emotional_score,
                    social_score,
                    creativity_score
                FROM child_development_trends
                WHERE child_id = %s
                ORDER BY date ASC
            """, (child_id,))
            
            all_trends = []
            for row in cursor.fetchall():
                all_trends.append({
                    'date': str(row[0]),
                    'vocabulary_size': int(row[1]) if row[1] else 0,
                    'sentence_complexity': float(row[2]) if row[2] else 0,
                    'language': float(row[3]) if row[3] else 0,
                    'cognitive': float(row[4]) if row[4] else 0,
                    'emotional': float(row[5]) if row[5] else 0,
                    'social': float(row[6]) if row[6] else 0,
                    'creativity': float(row[7]) if row[7] else 0
                })
            
            # Calculate consistency (sessions per week)
            cursor.execute("""
                SELECT COUNT(DISTINCT DATE(timestamp)) as days_with_sessions
                FROM child_development_sessions
                WHERE child_id = %s
                AND timestamp >= DATEADD(day, -30, CURRENT_TIMESTAMP())
            """, (child_id,))
            
            days_with_sessions = cursor.fetchone()[0] or 0
            consistency = days_with_sessions / 30.0  # Sessions per day over 30 days
            
            cursor.close()
            
            # Format trends for frontend (with date and value)
            vocabulary_growth = [
                {'date': t['date'], 'value': t['vocabulary_size']}
                for t in all_trends
            ]
            complexity_progression = [
                {'date': t['date'], 'value': t['sentence_complexity']}
                for t in all_trends
            ]
            
            return {
                'vocabulary_growth': vocabulary_growth,
                'complexity_progression': complexity_progression,
                'consistency': consistency,
                'timeline': all_trends,
                'trend_direction': self._calculate_trend_direction(all_trends)
            }
        except Exception as e:
            logger.error(f"Error getting longitudinal analysis: {e}")
            return {}
    
    def _calculate_trend_direction(self, trends: List[Dict]) -> str:
        """Calculate overall trend direction"""
        if len(trends) < 2:
            return 'insufficient_data'
        
        recent_avg = sum(t.get('language', 0) for t in trends[-7:]) / min(7, len(trends))
        older_avg = sum(t.get('language', 0) for t in trends[:7]) / min(7, len(trends))
        
        if recent_avg > older_avg * 1.1:
            return 'improving'
        elif recent_avg < older_avg * 0.9:
            return 'declining'
        else:
            return 'stable'
    
    def close(self):
        """Close Snowflake connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

