#!/usr/bin/env python3
"""
HoloMentor Mobile AR - Flask Backend
Modular AI voice assistant API for mobile (React Native) and future Unity integration
"""

import os
import json
import uuid
import logging
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# Import custom modules
from services.gemini_service import GeminiService
from services.claude_service import ClaudeService
from services.elevenlabs_service import ElevenLabsService
from services.firebase_service import FirebaseService
from services.whisper_service import WhisperService
from services.emotion_service import EmotionService
from services.snowflake_service import SnowflakeService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for mobile app

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'storage/audio'
app.config['SESSION_FOLDER'] = 'storage/sessions'

# Initialize services
gemini_service = GeminiService()
claude_service = ClaudeService()
elevenlabs_service = ElevenLabsService()
firebase_service = FirebaseService()
whisper_service = WhisperService()
emotion_service = EmotionService()
snowflake_service = SnowflakeService()

# Ensure storage directories exist
Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
Path(app.config['SESSION_FOLDER']).mkdir(parents=True, exist_ok=True)
Path('storage/audio/tts').mkdir(parents=True, exist_ok=True)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'HoloMentor Mobile AR',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'gemini': gemini_service.is_available(),
            'claude': claude_service.is_available(),
            'elevenlabs': elevenlabs_service.is_available(),
            'firebase': firebase_service.is_available(),
            'whisper': whisper_service.is_available(),
            'snowflake': snowflake_service.is_available()
        }
    })


@app.route('/api/ask', methods=['POST'])
def ask_question():
    """
    Core AI voice assistant endpoint
    Takes user_input, calls Groq Llama 3 70B, generates ElevenLabs TTS audio
    Returns: { text, audio_url, emotion }
    
    Request:
    {
        "user_input": "What is photosynthesis?",
        "user_id": "optional",
        "context": {}
    }
    
    Response:
    {
        "text": "Photosynthesis is...",
        "audio_url": "/api/audio/tts/abc123.mp3",
        "emotion": "curious"
    }
    """
    try:
        data = request.json
        user_id = data.get('user_id', 'anonymous')
        user_input = data.get('user_input', '') or data.get('question', '')  # Support both field names
        context = data.get('context', {})
        
        if not user_input:
            return jsonify({'error': 'No user_input provided'}), 400
        
        # Get user profile for personalization
        user_profile = None
        if user_id != 'anonymous':
            user_profile = firebase_service.get_user(user_id)
        
        # Build personalized context
        system_context = build_personalized_context(user_profile, context)
        
        # Get fast response from Gemini
        logger.info(f"Processing question from {user_id}: {user_input}")
        response = gemini_service.get_response(
            question=user_input,
            system_context=system_context,
            user_profile=user_profile
        )
        
        # Detect emotion from user input (simple text-based analysis)
        emotion_analysis = emotion_service.analyze_text(user_input)
        detected_emotion = emotion_analysis.get('primary_emotion', 'neutral')
        
        # Generate natural speech with ElevenLabs
        audio_response = elevenlabs_service.text_to_speech(
            text=response['answer'],
            voice_id=user_profile.get('preferences', {}).get('voice_id', 'default') if user_profile else 'default'
        )
        
        # Build full audio URL (for mobile app)
        base_url = request.host_url.rstrip('/')
        full_audio_url = f"{base_url}{audio_response['audio_url']}"
        
        # Save interaction to Firebase (optional)
        if user_id != 'anonymous':
            firebase_service.log_interaction(
                user_id=user_id,
                interaction_type='question',
                question=user_input,
                response=response['answer'],
                context=context
            )
        
        # Log interaction to Snowflake for analytics
        import uuid
        session_id = request.headers.get('X-Session-ID', str(uuid.uuid4()))
        interaction_id = str(uuid.uuid4())
        
        if snowflake_service.is_available():
            snowflake_service.log_interaction(
                user_id=user_id,
                session_id=session_id,
                interaction_data={
                    'interaction_id': interaction_id,
                    'type': 'question',
                    'user_input': user_input,
                    'ai_response': response['answer'],
                    'emotion': detected_emotion,
                    'response_time': response.get('response_time', 0),
                    'audio_duration': audio_response.get('duration', 0),
                    'model': 'gemini',
                    'metadata': {
                        'voice_id': user_profile.get('preferences', {}).get('voice_id', 'default') if user_profile else 'default',
                        'context_length': len(context) if context else 0
                    }
                }
            )
        
        logger.info(f"Generated response for {user_id} - Emotion: {detected_emotion}")
        
        # Return in the exact format requested for mobile app
        return jsonify({
            'text': response['answer'],
            'audio_url': full_audio_url,  # Full URL for mobile app
            'emotion': detected_emotion,
            # Additional metadata (optional, for debugging)
            'response_time': response.get('response_time', 0),
            'audio_duration': audio_response.get('duration', 0),
            'interaction_id': interaction_id,
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Error in /api/ask: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/audio/tts/<filename>', methods=['GET'])
def serve_audio(filename):
    """Serve TTS audio files"""
    try:
        audio_path = Path('storage/audio/tts') / filename
        if audio_path.exists():
            return send_file(str(audio_path), mimetype='audio/mpeg')
        else:
            return jsonify({'error': 'Audio file not found'}), 404
    except Exception as e:
        logger.error(f"Error serving audio: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/plan', methods=['POST'])
def generate_plan():
    """
    Structured lesson-plan or quiz generation using Claude 3 Sonnet
    For in-depth learning, curriculum planning, assessments
    """
    try:
        data = request.json
        user_id = data.get('user_id', 'anonymous')
        plan_type = data.get('plan_type', 'lesson')
        topic = data.get('topic', '')
        parameters = data.get('parameters', {})
        
        if not topic:
            return jsonify({'error': 'No topic provided'}), 400
        
        # Get user profile for personalization
        user_profile = None
        if user_id != 'anonymous':
            user_profile = firebase_service.get_user(user_id)
        
        # Generate structured plan with Claude 3 Sonnet
        logger.info(f"Generating {plan_type} plan for {user_id}: {topic}")
        
        if plan_type == 'lesson':
            plan = claude_service.generate_lesson_plan(
                topic=topic,
                user_profile=user_profile,
                parameters=parameters
            )
        elif plan_type == 'quiz':
            plan = claude_service.generate_quiz(
                topic=topic,
                user_profile=user_profile,
                parameters=parameters
            )
        elif plan_type == 'curriculum':
            plan = claude_service.generate_curriculum(
                topic=topic,
                user_profile=user_profile,
                parameters=parameters
            )
        else:
            return jsonify({'error': f'Invalid plan_type: {plan_type}'}), 400
        
        # Generate audio introduction for the plan
        intro_text = plan.get('introduction', plan.get('overview', ''))
        if intro_text:
            audio_intro = elevenlabs_service.text_to_speech(
                text=intro_text,
                voice_id=user_profile.get('preferences', {}).get('voice_id', 'default') if user_profile else 'default'
            )
            base_url = request.host_url.rstrip('/')
            plan['audio_intro_url'] = f"{base_url}{audio_intro['audio_url']}"
        
        # Save plan to Firebase
        if user_id != 'anonymous':
            plan_id = firebase_service.save_learning_plan(
                user_id=user_id,
                plan_type=plan_type,
                topic=topic,
                plan_data=plan
            )
            plan['plan_id'] = plan_id
        
        logger.info(f"Generated {plan_type} plan for {user_id}")
        
        return jsonify({
            'success': True,
            'plan_type': plan_type,
            'plan': plan
        })
        
    except Exception as e:
        logger.error(f"Error in /api/plan: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/user/profile', methods=['GET', 'POST', 'PUT'])
def user_profile():
    """Get, create, or update user profile"""
    try:
        user_id = request.headers.get('X-User-ID', request.args.get('user_id', 'anonymous'))
        
        if request.method == 'GET':
            # Get user profile
            profile = firebase_service.get_user_profile(user_id) if firebase_service.is_available() else {}
            
            # Enhance with Snowflake data if available
            if snowflake_service.is_available():
                insights = snowflake_service.get_user_insights(user_id, days=30)
                profile['analytics'] = insights
            
            return jsonify(profile)
        
        elif request.method == 'POST' or request.method == 'PUT':
            # Create or update user profile
            data = request.get_json() or {}
            
            profile_data = {
                'name': data.get('name'),
                'age': data.get('age'),
                'learning_goals': data.get('learning_goals', []),
                'preferences': data.get('preferences', {})
            }
            
            # Save to Firebase
            if firebase_service.is_available():
                firebase_service.update_user_profile(user_id, profile_data)
            
            # Save to Snowflake
            if snowflake_service.is_available():
                snowflake_service.update_user_profile(user_id, profile_data)
            
            return jsonify({
                'success': True,
                'user_id': user_id,
                'profile': profile_data
            })
        
    except Exception as e:
        logger.error(f"Error in /api/user/profile: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    """Get comprehensive dashboard data with AI insights"""
    try:
        user_id = request.headers.get('X-User-ID', request.args.get('user_id', 'anonymous'))
        days = int(request.args.get('days', 30))
        
        if user_id == 'anonymous':
            return jsonify({
                'error': 'User ID required for dashboard',
                'message': 'Please provide X-User-ID header or user_id query parameter'
            }), 400
        
        # Get dashboard data from Snowflake
        if snowflake_service.is_available():
            dashboard_data = snowflake_service.get_dashboard_data(user_id)
            
            # Enhance with Firebase profile if available
            if firebase_service.is_available():
                profile = firebase_service.get_user_profile(user_id)
                dashboard_data['profile'] = profile
            
            return jsonify(dashboard_data)
        else:
            # Fallback to Firebase-only data
            profile = firebase_service.get_user_profile(user_id) if firebase_service.is_available() else {}
            return jsonify({
                'user_id': user_id,
                'message': 'Snowflake not configured - limited analytics available',
                'profile': profile,
                'summary': {
                    'total_interactions': 0,
                    'active_days': 0,
                    'engagement_score': 0.5
                },
                'ai_insights': ['Configure Snowflake for detailed analytics and AI insights']
            })
        
    except Exception as e:
        logger.error(f"Error in /api/dashboard: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/insights', methods=['GET'])
def analytics_insights():
    """Get AI-powered insights for a user"""
    try:
        user_id = request.headers.get('X-User-ID', request.args.get('user_id', 'anonymous'))
        days = int(request.args.get('days', 30))
        
        if user_id == 'anonymous':
            return jsonify({
                'error': 'User ID required for insights',
                'message': 'Please provide X-User-ID header or user_id query parameter'
            }), 400
        
        if snowflake_service.is_available():
            insights = snowflake_service.get_user_insights(user_id, days=days)
            return jsonify(insights)
        else:
            return jsonify({
                'error': 'Snowflake not configured',
                'message': 'Configure Snowflake to enable AI insights'
            }), 503
        
    except Exception as e:
        logger.error(f"Error in /api/analytics/insights: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/conversations', methods=['GET'])
def analytics_conversations():
    """Get conversation history for analytics"""
    try:
        user_id = request.headers.get('X-User-ID', request.args.get('user_id', 'anonymous'))
        limit = int(request.args.get('limit', 50))
        
        if user_id == 'anonymous':
            return jsonify({
                'error': 'User ID required',
                'message': 'Please provide X-User-ID header or user_id query parameter'
            }), 400
        
        # Get from Firebase (primary source for conversations)
        if firebase_service.is_available():
            conversations = firebase_service.get_user_interactions(user_id, limit=limit)
            return jsonify({
                'user_id': user_id,
                'conversations': conversations,
                'total': len(conversations)
            })
        else:
            return jsonify({
                'error': 'Firebase not configured',
                'message': 'Configure Firebase to access conversation history'
            }), 503
        
    except Exception as e:
        logger.error(f"Error in /api/analytics/conversations: {e}")
        return jsonify({'error': str(e)}), 500


def build_personalized_context(user_profile, additional_context):
    """Build personalized context for AI responses using user data and analytics"""
    context = {
        'role': 'You are HoloMentor, an AI holographic learning companion. You are patient, encouraging, and adaptive.',
        'personality': 'friendly, supportive, and educational'
    }
    
    if user_profile:
        context['student_name'] = user_profile.get('name')
        context['age'] = user_profile.get('age')
        context['learning_goals'] = user_profile.get('learning_goals', [])
        context['difficulty_level'] = user_profile.get('preferences', {}).get('difficulty_level', 'beginner')
        context['learning_progress'] = user_profile.get('learning_progress', {})
        context['emotional_state'] = user_profile.get('emotional_trends', {}).get('overall_mood', 'neutral')
        
        # Enhance with Snowflake analytics if available
        if snowflake_service.is_available():
            user_id = user_profile.get('user_id', 'anonymous')
            insights = snowflake_service.get_user_insights(user_id, days=30)
            
            if insights:
                context['analytics'] = {
                    'total_interactions': insights.get('total_interactions', 0),
                    'engagement_score': insights.get('engagement_score', 0.5),
                    'most_common_emotion': insights.get('most_common_emotion', 'neutral'),
                    'topics_covered': insights.get('topics_covered', [])[:5]  # Recent topics
                }
                
                # Add personalized learning recommendations
                recommendations = insights.get('insights', [])
                if recommendations:
                    context['learning_insights'] = recommendations[:3]  # Top 3 insights
    
    context.update(additional_context)
    return context


if __name__ == '__main__':
    logger.info("🚀 Starting HoloMentor Mobile AR Backend")
    logger.info(f"🤖 Gemini: {'✓' if gemini_service.is_available() else '✗'}")
    logger.info(f"🤖 Claude: {'✓' if claude_service.is_available() else '✗'}")
    logger.info(f"🔊 ElevenLabs: {'✓' if elevenlabs_service.is_available() else '✗'}")
    logger.info(f"🔥 Firebase: {'✓' if firebase_service.is_available() else '✗'}")
    logger.info(f"🎤 Whisper: {'✓' if whisper_service.is_available() else '✗'}")
    logger.info(f"❄️  Snowflake: {'✓' if snowflake_service.is_available() else '✗'}")
    
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')  # Allow connections from mobile devices on same network
    
    logger.info(f"🌐 Server starting on http://{host}:{port}")
    logger.info(f"📱 Mobile app can connect at: http://YOUR_IP:{port}")
    
    app.run(host=host, port=port, debug=os.environ.get('DEBUG', 'False') == 'True')

