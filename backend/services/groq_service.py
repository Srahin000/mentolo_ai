"""
Groq Llama 3 70B Service - Fast Real-time AI Responses
"""

import os
import time
import logging
from groq import Groq

logger = logging.getLogger(__name__)


class GroqService:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.client = None
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info("Groq service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Groq: {e}")
    
    def is_available(self):
        """Check if Groq service is available"""
        return self.client is not None
    
    def get_response(self, question, system_context, user_profile=None):
        """
        Get fast response from Groq Llama 3 70B
        Optimized for real-time conversational AI
        """
        if not self.client:
            raise Exception("Groq service not available")
        
        try:
            start_time = time.time()
            
            # Build system prompt
            system_prompt = self._build_system_prompt(system_context, user_profile)
            
            # Call Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                model="llama3-70b-8192",  # Fast, high-quality model
                temperature=0.7,
                max_tokens=1024,
                top_p=0.9,
                stream=False
            )
            
            response_time = time.time() - start_time
            
            answer = chat_completion.choices[0].message.content
            
            # Extract thinking points and follow-up questions
            thinking_points, follow_ups = self._extract_metadata(answer)
            
            logger.info(f"Groq response generated in {response_time:.2f}s")
            
            return {
                'answer': answer,
                'thinking_points': thinking_points,
                'follow_up_questions': follow_ups,
                'response_time': response_time,
                'model': 'llama3-70b-8192'
            }
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise
    
    def generate_greeting(self, user_profile):
        """Generate personalized greeting for AR session"""
        if not self.client:
            return "Hello! I'm HoloMentor, your AI learning companion. How can I help you today?"
        
        try:
            name = user_profile.get('name', 'there')
            learning_goals = user_profile.get('learning_goals', [])
            
            prompt = f"Generate a warm, brief greeting (2-3 sentences) for {name}."
            if learning_goals:
                prompt += f" They're interested in learning about: {', '.join(learning_goals[:3])}."
            prompt += " Be encouraging and friendly."
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are HoloMentor, a friendly AI holographic tutor. Generate warm, brief greetings."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama3-70b-8192",
                temperature=0.8,
                max_tokens=150
            )
            
            return chat_completion.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating greeting: {e}")
            return f"Hello {user_profile.get('name', 'there')}! Ready to learn something amazing today?"
    
    def _build_system_prompt(self, context, user_profile):
        """Build personalized system prompt"""
        prompt = context.get('role', 'You are HoloMentor, an AI holographic learning companion.')
        prompt += f"\n\nPersonality: {context.get('personality', 'friendly and educational')}"
        
        if user_profile:
            name = context.get('student_name')
            if name:
                prompt += f"\n\nYou are speaking with {name}."
            
            age = context.get('age')
            if age:
                prompt += f" They are {age} years old."
            
            difficulty = context.get('difficulty_level', 'beginner')
            prompt += f"\n\nAdapt your explanations for a {difficulty} level learner."
            
            learning_goals = context.get('learning_goals')
            if learning_goals:
                prompt += f"\n\nTheir learning goals include: {', '.join(learning_goals)}"
            
            emotional_state = context.get('emotional_state', 'neutral')
            if emotional_state in ['frustrated', 'confused']:
                prompt += f"\n\nThe student seems {emotional_state}. Be extra patient and encouraging."
            elif emotional_state in ['excited', 'engaged']:
                prompt += f"\n\nThe student is {emotional_state}! Match their energy and enthusiasm."
        
        prompt += "\n\nProvide clear, concise, engaging responses. Use examples when helpful. Ask follow-up questions to check understanding."
        
        return prompt
    
    def _extract_metadata(self, answer):
        """Extract thinking points and follow-up questions from response"""
        thinking_points = []
        follow_ups = []
        
        # Simple extraction (could be enhanced with more sophisticated parsing)
        lines = answer.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('*') or line.startswith('-') or line.startswith('•'):
                thinking_points.append(line.lstrip('*-• '))
            elif '?' in line and len(line) < 150:
                follow_ups.append(line)
        
        return thinking_points[:3], follow_ups[:2]

