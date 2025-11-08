"""
Child Development Analysis Service
Uses Gemini Pro for holistic child development analysis from conversation transcripts
"""

import os
import logging
import json
from typing import Dict, List, Optional
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class ChildDevelopmentService:
    def __init__(self):
        # Use Pro model for detailed child development analysis
        self.gemini_service = GeminiService(use_pro_model=True)
    
    def analyze_session(self, transcript: str, child_age: int, child_name: str, 
                       session_context: Dict = None) -> Dict:
        """
        Analyze a conversation session for child development insights
        
        Args:
            transcript: Full conversation transcript
            child_age: Child's age in years
            child_name: Child's name
            session_context: Additional context (duration, known interests, etc.)
        
        Returns:
            Dict with comprehensive development analysis
        """
        if not self.gemini_service.is_available():
            raise Exception("Gemini service not available")
        
        # Build analysis prompt
        prompt = self._build_analysis_prompt(
            transcript=transcript,
            child_age=child_age,
            child_name=child_name,
            context=session_context or {}
        )
        
        # Get analysis from Gemini
        response = self.gemini_service.get_response(
            question=prompt,
            system_context={'role': 'Child Development Analyst'},
            user_profile=None
        )
        
        # Parse JSON response
        analysis = self._parse_analysis(response['answer'])
        
        return analysis
    
    def _build_analysis_prompt(self, transcript: str, child_age: int, 
                               child_name: str, context: Dict) -> str:
        """Build the analysis prompt for Gemini"""
        known_interests = context.get('known_interests', [])
        duration = context.get('duration_minutes', 'unknown')
        
        prompt = f"""You are an expert child development analyst specializing in early childhood development. Analyze this conversation transcript between a parent and their {child_age}-year-old child named {child_name}.

TRANSCRIPT:
{transcript}

CONTEXT:
- Child Age: {child_age} years old
- Session Duration: {duration} minutes
- Previous Interests: {', '.join(known_interests) if known_interests else 'None recorded'}

Analyze this conversation and provide a comprehensive development assessment. Return ONLY valid JSON in this exact structure (no markdown, no code blocks, just pure JSON):

{{
  "daily_insight": "One compelling parent-friendly observation (2-3 sentences)",
  "development_snapshot": {{
    "language": {{"level": "growing|strong|emerging", "score": 0-100}},
    "cognitive": {{"level": "growing|strong|emerging", "score": 0-100}},
    "emotional": {{"level": "growing|strong|emerging", "score": 0-100}},
    "social": {{"level": "growing|strong|emerging", "score": 0-100}},
    "creativity": {{"level": "growing|strong|emerging", "score": 0-100}}
  }},
  "strengths": [
    {{
      "title": "Superpower name",
      "evidence": "Specific example from transcript",
      "why_matters": "Why this strength is important"
    }}
  ],
  "growth_opportunities": [
    {{
      "area": "Skill name",
      "current": "Where they are now",
      "next_step": "How to improve"
    }}
  ],
  "personalized_activities": [
    {{
      "title": "Activity name",
      "duration": "10 minutes",
      "materials": ["item1", "item2"],
      "instructions": "Step-by-step instructions",
      "impact_areas": ["language", "emotional"],
      "based_on_interests": ["child's interests from transcript or context"]
    }}
  ],
  "conversation_starters": [
    "Question to ask child",
    "Another question"
  ],
  "milestone_progress": {{
    "on_track": ["skill1", "skill2"],
    "emerging": ["skill3"],
    "ahead": ["skill4"]
  }},
  "parent_encouragement": "Positive reinforcement message",
  "vocabulary_analysis": {{
    "new_words_used": ["word1", "word2"],
    "vocabulary_size_estimate": 850,
    "sentence_complexity": 7.2,
    "question_frequency": 12
  }},
  "cognitive_indicators": {{
    "reasoning_language": ["because", "so", "if-then"],
    "abstract_concepts": ["pretend", "imagine"],
    "problem_solving_attempts": 8,
    "curiosity_score": 85
  }},
  "emotional_intelligence": {{
    "emotion_words_used": ["happy", "sad"],
    "empathy_indicators": ["she feels", "he wants"],
    "self_awareness": ["I think", "I feel"],
    "emotional_regulation": "developing|strong|emerging"
  }},
  "social_skills": {{
    "turn_taking": "appropriate|developing",
    "politeness_markers": ["please", "thank you"],
    "perspective_taking": "emerging|strong",
    "sharing_language": ["we can", "let's"]
  }},
  "creativity_imagination": {{
    "pretend_play_language": ["let's pretend"],
    "novel_word_combinations": 15,
    "storytelling_originality": "high|medium|low",
    "humor_attempts": 3
  }},
  "speech_clarity": {{
    "intelligibility": 88,
    "age_appropriate": true,
    "sounds_to_practice": ["r", "th"],
    "fluency": "smooth|developing"
  }}
}}

Focus on:
1. Specific examples from the transcript
2. Age-appropriate milestones for {child_age}-year-olds
3. Actionable insights for parents
4. Positive, encouraging tone
5. Evidence-based observations

Return ONLY the JSON, no additional text or explanation."""
        
        return prompt
    
    def _parse_analysis(self, response_text: str) -> Dict:
        """Parse Gemini response into structured analysis"""
        try:
            # Extract JSON from response (handle markdown code blocks)
            text = response_text.strip()
            
            # Remove markdown code blocks if present
            if '```json' in text:
                json_start = text.find('```json') + 7
                json_end = text.find('```', json_start)
                text = text[json_start:json_end].strip()
            elif '```' in text:
                json_start = text.find('```') + 3
                json_end = text.find('```', json_start)
                if json_end > json_start:
                    text = text[json_start:json_end].strip()
            
            # Try to find JSON object boundaries
            if '{' in text and '}' in text:
                start = text.find('{')
                end = text.rfind('}') + 1
                text = text[start:end]
            
            analysis = json.loads(text)
            
            # Validate structure
            self._validate_analysis(analysis)
            
            return analysis
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse analysis JSON: {e}")
            logger.error(f"Response text (first 500 chars): {response_text[:500]}")
            # Return fallback structure
            return self._get_fallback_analysis()
        except Exception as e:
            logger.error(f"Error parsing analysis: {e}")
            return self._get_fallback_analysis()
    
    def _validate_analysis(self, analysis: Dict):
        """Validate analysis structure has required fields"""
        required_fields = [
            'daily_insight',
            'development_snapshot',
            'strengths',
            'growth_opportunities',
            'personalized_activities'
        ]
        
        for field in required_fields:
            if field not in analysis:
                logger.warning(f"Missing field in analysis: {field}")
                if field == 'development_snapshot':
                    analysis[field] = {}
                elif field in ['strengths', 'growth_opportunities', 'personalized_activities']:
                    analysis[field] = []
                else:
                    analysis[field] = ""
    
    def _get_fallback_analysis(self) -> Dict:
        """Return fallback analysis structure if parsing fails"""
        return {
            "daily_insight": "Great conversation! Keep engaging with your child to see detailed insights.",
            "development_snapshot": {
                "language": {"level": "growing", "score": 70},
                "cognitive": {"level": "growing", "score": 70},
                "emotional": {"level": "growing", "score": 70},
                "social": {"level": "growing", "score": 70},
                "creativity": {"level": "growing", "score": 70}
            },
            "strengths": [],
            "growth_opportunities": [],
            "personalized_activities": [],
            "conversation_starters": [],
            "milestone_progress": {"on_track": [], "emerging": [], "ahead": []},
            "parent_encouragement": "Keep up the great work! Regular conversations help track development.",
            "vocabulary_analysis": {
                "new_words_used": [],
                "vocabulary_size_estimate": 0,
                "sentence_complexity": 0,
                "question_frequency": 0
            },
            "cognitive_indicators": {
                "reasoning_language": [],
                "abstract_concepts": [],
                "problem_solving_attempts": 0,
                "curiosity_score": 0
            },
            "emotional_intelligence": {
                "emotion_words_used": [],
                "empathy_indicators": [],
                "self_awareness": [],
                "emotional_regulation": "developing"
            },
            "social_skills": {
                "turn_taking": "developing",
                "politeness_markers": [],
                "perspective_taking": "emerging",
                "sharing_language": []
            },
            "creativity_imagination": {
                "pretend_play_language": [],
                "novel_word_combinations": 0,
                "storytelling_originality": "medium",
                "humor_attempts": 0
            },
            "speech_clarity": {
                "intelligibility": 0,
                "age_appropriate": True,
                "sounds_to_practice": [],
                "fluency": "developing"
            }
        }

