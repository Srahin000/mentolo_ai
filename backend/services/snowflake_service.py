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
                    preferences_json VARIANT
                )
            """)
            
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
                cursor.execute("""
                    UPDATE user_profiles
                    SET name = %s, age = %s, updated_at = %s,
                        learning_goals = %s, preferences_json = %s
                    WHERE user_id = %s
                """, (
                    profile_data.get('name'),
                    profile_data.get('age'),
                    datetime.now(timezone.utc),
                    json.dumps(profile_data.get('learning_goals', [])),
                    json.dumps(profile_data.get('preferences', {})),
                    user_id
                ))
            else:
                # Create new user
                cursor.execute("""
                    INSERT INTO user_profiles (
                        user_id, name, age, created_at, updated_at,
                        learning_goals, preferences_json
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    user_id,
                    profile_data.get('name'),
                    profile_data.get('age'),
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc),
                    json.dumps(profile_data.get('learning_goals', [])),
                    json.dumps(profile_data.get('preferences', {}))
                ))
            
            cursor.close()
            logger.info(f"Updated user profile in Snowflake: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating user profile in Snowflake: {e}")
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
            
            return {
                'total_interactions': stats[0] if stats else 0,
                'avg_response_time': float(stats[1]) if stats and stats[1] else 0,
                'avg_audio_duration': float(stats[2]) if stats and stats[2] else 0,
                'active_days': stats[3] if stats else 0,
                'most_common_emotion': stats[4] if stats else 'neutral',
                'topics_covered': topics[:10],  # Last 10 topics
                'progress_timeline': progress_data,
                'engagement_score': self._calculate_engagement(stats, progress_data),
                'insights': self._generate_ai_insights(stats, progress_data, topics)
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
    
    def _generate_ai_insights(self, stats, progress_data, topics) -> List[str]:
        """Generate AI-powered insights from user data"""
        insights = []
        
        if not stats:
            return ["Start learning to see personalized insights!"]
        
        total = stats[0]
        avg_time = float(stats[1]) if stats[1] else 0
        emotion = stats[4] if stats[4] else 'neutral'
        
        # Interaction frequency insights
        if total > 50:
            insights.append(f"🌟 Great progress! You've had {total} learning interactions.")
        elif total > 20:
            insights.append(f"📈 You're building a good learning habit with {total} interactions.")
        else:
            insights.append(f"💪 Keep going! You've started with {total} interactions.")
        
        # Response time insights
        if avg_time < 1.0:
            insights.append("⚡ Fast responses show you're asking great questions!")
        elif avg_time > 2.0:
            insights.append("🤔 Complex questions take more time - that's great for deep learning!")
        
        # Emotion insights
        if emotion == 'excited':
            insights.append("😊 Your enthusiasm is showing! Keep that energy!")
        elif emotion == 'confused':
            insights.append("💡 It's okay to be confused - that's when real learning happens!")
        
        # Progress insights
        if progress_data and len(progress_data) > 7:
            recent_avg = sum(p['interactions'] for p in progress_data[:7]) / 7
            older_avg = sum(p['interactions'] for p in progress_data[7:14]) / 7 if len(progress_data) > 14 else recent_avg
            
            if recent_avg > older_avg * 1.2:
                insights.append("📊 Your learning activity is increasing - excellent momentum!")
        
        return insights
    
    def get_dashboard_data(self, user_id: str) -> Dict:
        """Get comprehensive dashboard data"""
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
            'ai_insights': insights.get('insights', []),
            'recommendations': self._generate_recommendations(insights)
        }
    
    def _generate_recommendations(self, insights: Dict) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
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
        
        return recommendations
    
    def close(self):
        """Close Snowflake connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

