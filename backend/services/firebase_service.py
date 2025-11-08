"""
Firebase Firestore Service - User Profiles, Progress Tracking, Emotional Trends
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger(__name__)


class FirebaseService:
    def __init__(self):
        self.db = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if already initialized
            if firebase_admin._apps:
                self.db = firestore.client()
                logger.info("Firebase already initialized")
                return
            
            # Initialize with credentials
            cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
            
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                # Try to initialize with default credentials
                firebase_admin.initialize_app()
            
            self.db = firestore.client()
            logger.info("Firebase service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            self.db = None
    
    def is_available(self):
        """Check if Firebase service is available"""
        return self.db is not None
    
    # ===== User Profile Management =====
    
    def create_user(self, user_id: str, user_data: Dict):
        """Create a new user profile"""
        if not self.db:
            raise Exception("Firebase not available")
        
        try:
            self.db.collection('users').document(user_id).set(user_data)
            logger.info(f"Created user: {user_id}")
            return user_id
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user profile"""
        if not self.db:
            return None
        
        try:
            doc = self.db.collection('users').document(user_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def update_user(self, user_id: str, updates: Dict):
        """Update user profile"""
        if not self.db:
            raise Exception("Firebase not available")
        
        try:
            updates['updated_at'] = datetime.utcnow().isoformat()
            self.db.collection('users').document(user_id).update(updates)
            logger.info(f"Updated user: {user_id}")
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise
    
    # ===== Interaction Logging =====
    
    def log_interaction(self, user_id: str, interaction_type: str, question: str, 
                       response: str, context: Dict):
        """Log user interaction"""
        if not self.db:
            return
        
        try:
            interaction_data = {
                'user_id': user_id,
                'type': interaction_type,
                'question': question,
                'response': response,
                'context': context,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Add to interactions collection
            self.db.collection('interactions').add(interaction_data)
            
            # Increment user session count
            user_ref = self.db.collection('users').document(user_id)
            user_ref.update({
                'total_sessions': firestore.Increment(1),
                'last_interaction': datetime.utcnow().isoformat()
            })
            
            logger.info(f"Logged interaction for user: {user_id}")
        except Exception as e:
            logger.error(f"Error logging interaction: {e}")
    
    def get_recent_interactions(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent interactions for a user"""
        if not self.db:
            return []
        
        try:
            interactions = (
                self.db.collection('interactions')
                .where('user_id', '==', user_id)
                .order_by('timestamp', direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )
            
            return [interaction.to_dict() for interaction in interactions]
        except Exception as e:
            logger.error(f"Error getting interactions: {e}")
            return []
    
    # ===== Emotional Trends =====
    
    def update_emotion_trends(self, user_id: str, emotion_data: Dict):
        """Update user emotional trends"""
        if not self.db:
            return
        
        try:
            # Add emotion record
            emotion_record = {
                'user_id': user_id,
                'emotion': emotion_data.get('primary_emotion'),
                'confidence': emotion_data.get('confidence', 0.5),
                'valence': emotion_data.get('valence', 0.5),
                'arousal': emotion_data.get('arousal', 0.5),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.db.collection('emotions').add(emotion_record)
            
            # Update aggregate trends in user profile
            user_ref = self.db.collection('users').document(user_id)
            user_ref.update({
                'emotional_trends.last_emotion': emotion_data.get('primary_emotion'),
                'emotional_trends.last_update': datetime.utcnow().isoformat()
            })
            
            logger.info(f"Updated emotion trends for user: {user_id}")
        except Exception as e:
            logger.error(f"Error updating emotion trends: {e}")
    
    def get_emotion_trends(self, user_id: str, days: int = 7) -> Dict:
        """Get emotional trends over time"""
        if not self.db:
            return {}
        
        try:
            # Get emotions from last N days
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            emotions = (
                self.db.collection('emotions')
                .where('user_id', '==', user_id)
                .where('timestamp', '>=', cutoff_date.isoformat())
                .stream()
            )
            
            emotion_list = [e.to_dict() for e in emotions]
            
            # Calculate trends
            if not emotion_list:
                return {'overall_mood': 'neutral', 'engagement_score': 0.5}
            
            avg_valence = sum(e.get('valence', 0.5) for e in emotion_list) / len(emotion_list)
            avg_arousal = sum(e.get('arousal', 0.5) for e in emotion_list) / len(emotion_list)
            
            return {
                'overall_mood': self._valence_to_mood(avg_valence),
                'engagement_score': avg_arousal,
                'confidence_level': avg_valence,
                'total_data_points': len(emotion_list)
            }
        except Exception as e:
            logger.error(f"Error getting emotion trends: {e}")
            return {'overall_mood': 'neutral', 'engagement_score': 0.5}
    
    # ===== Learning Progress =====
    
    def update_learning_progress(self, user_id: str, topic: str, score: float):
        """Update learning progress for a topic"""
        if not self.db:
            return
        
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_ref.update({
                f'learning_progress.{topic}': score,
                'updated_at': datetime.utcnow().isoformat()
            })
            
            logger.info(f"Updated progress for {user_id} on {topic}: {score}")
        except Exception as e:
            logger.error(f"Error updating progress: {e}")
    
    def get_learning_progress(self, user_id: str) -> Dict:
        """Get detailed learning progress"""
        user = self.get_user(user_id)
        if user:
            return user.get('learning_progress', {})
        return {}
    
    # ===== Learning Plans =====
    
    def save_learning_plan(self, user_id: str, plan_type: str, topic: str, plan_data: Dict) -> str:
        """Save a learning plan"""
        if not self.db:
            raise Exception("Firebase not available")
        
        try:
            plan_record = {
                'user_id': user_id,
                'plan_type': plan_type,
                'topic': topic,
                'plan_data': plan_data,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'active'
            }
            
            doc_ref = self.db.collection('learning_plans').add(plan_record)
            plan_id = doc_ref[1].id
            
            logger.info(f"Saved learning plan: {plan_id}")
            return plan_id
        except Exception as e:
            logger.error(f"Error saving learning plan: {e}")
            raise
    
    # ===== Sessions =====
    
    def create_session(self, user_id: str) -> str:
        """Create a new learning session"""
        if not self.db:
            raise Exception("Firebase not available")
        
        try:
            session_data = {
                'user_id': user_id,
                'start_time': datetime.utcnow().isoformat(),
                'interactions': [],
                'status': 'active'
            }
            
            doc_ref = self.db.collection('sessions').add(session_data)
            session_id = doc_ref[1].id
            
            logger.info(f"Created session: {session_id}")
            return session_id
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
    
    def log_avatar_interaction(self, user_id: str, state: str, metadata: Dict):
        """Log avatar state for analytics"""
        if not self.db:
            return
        
        try:
            avatar_data = {
                'user_id': user_id,
                'state': state,
                'metadata': metadata,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.db.collection('avatar_interactions').add(avatar_data)
        except Exception as e:
            logger.error(f"Error logging avatar interaction: {e}")
    
    # ===== Helper Methods =====
    
    def _valence_to_mood(self, valence: float) -> str:
        """Convert valence score to mood label"""
        if valence > 0.7:
            return 'happy'
        elif valence > 0.5:
            return 'content'
        elif valence > 0.3:
            return 'neutral'
        else:
            return 'frustrated'

