"""
Google Gemini Service - AI Text Generation
Uses regular Gemini API (not Vertex AI)
"""

import os
import time
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self, use_pro_model=False):
        self.api_key = os.getenv('GEMINI_API_KEY')
        # Use Flash for quick responses, Pro for detailed analysis
        if use_pro_model:
            self.model_name = os.getenv('VERTEX_MODEL_PRO', 'gemini-2.5-pro')
        else:
            self.model_name = os.getenv('VERTEX_MODEL', 'gemini-2.5-flash')
        self.model = None
        self.use_pro = use_pro_model
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # List available models first to see what's actually available
                models = genai.list_models()
                available_models = [m for m in models if 'generateContent' in m.supported_generation_methods]
                
                # Extract model names (remove "models/" prefix)
                available_names = [m.name.split('/')[-1] for m in available_models]
                logger.info(f"Available Gemini models: {', '.join(available_names[:5])}")
                
                # Select model based on use case
                if self.use_pro:
                    # For analysis: prioritize Pro models
                    pro_models = [name for name in available_names if 'pro' in name.lower()]
                    
                    if self.model_name in available_names:
                        self.model = genai.GenerativeModel(self.model_name)
                        logger.info(f"✅ Gemini Pro initialized for analysis: {self.model_name}")
                    elif pro_models:
                        self.model_name = pro_models[0]
                        self.model = genai.GenerativeModel(self.model_name)
                        logger.info(f"✅ Using Gemini Pro model: {self.model_name}")
                    else:
                        # Fallback to flash if no pro available
                        flash_models = [name for name in available_names if 'flash' in name.lower()]
                        if flash_models:
                            self.model_name = flash_models[0]
                            self.model = genai.GenerativeModel(self.model_name)
                            logger.warning(f"⚠️  Pro not available, using Flash: {self.model_name}")
                        else:
                            raise Exception("No available Gemini models found")
                else:
                    # For quick responses: prioritize Flash models
                    flash_models = [name for name in available_names if 'flash' in name.lower()]
                    
                    if self.model_name in available_names:
                        self.model = genai.GenerativeModel(self.model_name)
                        logger.info(f"✅ Gemini Flash initialized for quick responses: {self.model_name}")
                    elif flash_models:
                        self.model_name = flash_models[0]
                        self.model = genai.GenerativeModel(self.model_name)
                        logger.info(f"✅ Using Gemini Flash model: {self.model_name}")
                    else:
                        # Fallback to any available model
                        if available_names:
                            self.model_name = available_names[0]
                            self.model = genai.GenerativeModel(self.model_name)
                            logger.warning(f"⚠️  Using fallback model: {self.model_name}")
                        else:
                            raise Exception("No available Gemini models found")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
    
    def is_available(self):
        """Check if Gemini service is available"""
        return self.model is not None
    
    def get_response(self, question, system_context, user_profile=None):
        """
        Get response from Google Gemini
        Compatible with GroqService interface
        """
        if not self.model:
            raise Exception("Gemini service not available")
        
        try:
            start_time = time.time()
            
            # Build system prompt
            system_prompt = self._build_system_prompt(system_context, user_profile)
            
            # Combine system prompt and question
            full_prompt = f"{system_prompt}\n\nUser question: {question}"
            
            # Call Gemini API - optimized based on model type
            generation_config = {
                'temperature': 0.7,
                'top_p': 0.9,
            }
            
            # Flash: lower tokens for speed, Pro: higher tokens for detailed analysis
            if self.use_pro or 'pro' in self.model_name.lower():
                generation_config['max_output_tokens'] = 4096  # More tokens for detailed analysis
            else:
                generation_config['max_output_tokens'] = 1024  # Lower for faster Flash responses
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            answer = response.text
            
            response_time = time.time() - start_time
            
            # Extract thinking points and follow-up questions
            thinking_points, follow_ups = self._extract_metadata(answer)
            
            logger.info(f"Gemini response generated in {response_time:.2f}s")
            
            return {
                'answer': answer,
                'thinking_points': thinking_points,
                'follow_up_questions': follow_ups,
                'response_time': response_time,
                'model': self.model_name
            }
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    def get_response_from_audio(self, audio_path, system_context, user_profile=None):
        """
        Get response from Google Gemini using audio input directly
        Skips STT step - Gemini processes audio directly
        
        Args:
            audio_path: Path to audio file (MP3, WAV, AAC, etc.)
            system_context: Context for the conversation
            user_profile: Optional user profile for personalization
        """
        if not self.model:
            raise Exception("Gemini service not available")
        
        try:
            start_time = time.time()
            
            # Build system prompt
            system_prompt = self._build_system_prompt(system_context, user_profile)
            
            # Upload audio file to Gemini
            logger.info(f"Uploading audio file to Gemini: {audio_path}")
            audio_file = genai.upload_file(path=audio_path)
            
            try:
                # Call Gemini API with audio
                generation_config = {
                    'temperature': 0.7,
                    'top_p': 0.9,
                }
                
                # Flash: lower tokens for speed, Pro: higher tokens for detailed analysis
                if self.use_pro or 'pro' in self.model_name.lower():
                    generation_config['max_output_tokens'] = 4096
                else:
                    generation_config['max_output_tokens'] = 1024
                
                # Generate content with audio input
                response = self.model.generate_content(
                    [system_prompt, audio_file],
                    generation_config=generation_config
                )
                
                answer = response.text
                
                response_time = time.time() - start_time
                
                # Extract thinking points and follow-up questions
                thinking_points, follow_ups = self._extract_metadata(answer)
                
                logger.info(f"Gemini audio response generated in {response_time:.2f}s")
                
                return {
                    'answer': answer,
                    'thinking_points': thinking_points,
                    'follow_up_questions': follow_ups,
                    'response_time': response_time,
                    'model': self.model_name
                }
            finally:
                # Clean up uploaded file
                try:
                    genai.delete_file(audio_file.name)
                    logger.info("Cleaned up uploaded audio file")
                except Exception as cleanup_error:
                    logger.warning(f"Could not delete uploaded file: {cleanup_error}")
            
        except Exception as e:
            logger.error(f"Gemini audio API error: {e}")
            raise
    
    def generate_greeting(self, user_profile):
        """Generate personalized greeting for AR session"""
        if not self.model:
            return "Hello! I'm HoloMentor, your AI learning companion. How can I help you today?"
        
        try:
            name = user_profile.get('name', 'there')
            learning_goals = user_profile.get('learning_goals', [])
            
            prompt = f"Generate a warm, brief greeting (2-3 sentences) for {name}."
            if learning_goals:
                prompt += f" They're interested in learning about: {', '.join(learning_goals[:3])}."
            prompt += " Be encouraging and friendly."
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
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
        
        # Simple extraction
        lines = answer.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('*') or line.startswith('-') or line.startswith('•'):
                thinking_points.append(line.lstrip('*-• '))
            elif '?' in line and len(line) < 150:
                follow_ups.append(line)
        
        return thinking_points[:3], follow_ups[:2]

