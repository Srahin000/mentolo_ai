"""
Interest Detection Service - Extract user interests from conversations and preferences
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# Try to import GeminiService (may not be available)
try:
    from .gemini_service import GeminiService
    GEMINI_AVAILABLE = True
except ImportError:
    try:
        from services.gemini_service import GeminiService
        GEMINI_AVAILABLE = True
    except ImportError:
        GEMINI_AVAILABLE = False
        GeminiService = None


class InterestService:
    def __init__(self):
        self.gemini_service = None
        if GEMINI_AVAILABLE and GeminiService:
            try:
                self.gemini_service = GeminiService()
            except Exception as e:
                logger.warning(f"Could not initialize Gemini service for interest detection: {e}")
    
    def extract_interests_from_profile(self, user_profile: Dict) -> List[str]:
        """Extract interests from user profile"""
        interests = []
        
        if not user_profile:
            return interests
        
        # From learning_goals
        learning_goals = user_profile.get('learning_goals', [])
        if learning_goals:
            interests.extend(self._normalize_interests(learning_goals))
        
        # From preferences
        preferences = user_profile.get('preferences', {})
        if 'interests' in preferences:
            interests.extend(self._normalize_interests(preferences['interests']))
        
        # Remove duplicates and return
        return list(set(interests))
    
    def extract_interests_from_conversations(self, conversations: List[Dict]) -> List[str]:
        """Use Gemini to extract interests from conversation topics"""
        if not conversations:
            return []
        
        if not self.gemini_service or not self.gemini_service.is_available():
            # Fallback: simple keyword extraction
            return self._extract_interests_simple(conversations)
        
        try:
            # Get recent topics
            topics = []
            for conv in conversations[:10]:
                question = conv.get('question', '') or conv.get('user_input', '')
                response = conv.get('response', '') or conv.get('ai_response', '')
                if question or response:
                    topics.append(f"Q: {question}\nA: {response}")
            
            if not topics:
                return []
            
            topics_text = '\n'.join(topics)
            
            prompt = f"""Analyze the following learning conversations and extract specific interests or activities the user is interested in (e.g., karate, swimming, music, art, sports).

Conversations:
{topics_text}

Return only a comma-separated list of specific interests/activities (e.g., "karate, swimming, music"). If no clear interests are mentioned, return "none"."""
            
            response = self.gemini_service.model.generate_content(prompt)
            interests_text = response.text.strip().lower()
            
            if interests_text and interests_text != 'none':
                interests = [i.strip() for i in interests_text.split(',')]
                return self._normalize_interests(interests)
            
            return []
            
        except Exception as e:
            logger.error(f"Error extracting interests with Gemini: {e}")
            # Fallback to simple extraction
            return self._extract_interests_simple(conversations)
    
    def _extract_interests_simple(self, conversations: List[Dict]) -> List[str]:
        """Simple keyword-based interest extraction"""
        interest_keywords = {
            'karate': ['karate', 'martial arts', 'dojo', 'sensei'],
            'swimming': ['swimming', 'pool', 'aquatics'],
            'dance': ['dance', 'ballet', 'hip hop', 'salsa'],
            'music': ['music', 'guitar', 'piano', 'violin', 'instrument'],
            'yoga': ['yoga', 'meditation', 'mindfulness'],
            'art': ['art', 'painting', 'drawing', 'sketching'],
            'sports': ['basketball', 'tennis', 'soccer', 'football'],
            'cooking': ['cooking', 'baking', 'culinary', 'recipe'],
        }
        
        interests = []
        all_text = ' '.join([
            conv.get('question', '') + ' ' + conv.get('response', '')
            for conv in conversations[:10]
        ]).lower()
        
        for interest, keywords in interest_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                interests.append(interest)
        
        return self._normalize_interests(interests)
    
    def _normalize_interests(self, interests: List[str]) -> List[str]:
        """Normalize interest names"""
        normalized = []
        for interest in interests:
            if not interest:
                continue
            interest = interest.lower().strip()
            # Map variations to standard names
            mapping = {
                'martial arts': 'karate',
                'karate classes': 'karate',
                'swimming lessons': 'swimming',
                'dance classes': 'dance',
                'music lessons': 'music',
                'taekwondo': 'karate',
                'judo': 'karate',
            }
            normalized.append(mapping.get(interest, interest))
        return normalized

