#!/usr/bin/env python3
"""
HoloMentor AR - AI-Powered Holographic Learning Companion
Main Flask Application
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
from services.groq_service import GroqService
from services.claude_service import ClaudeService
from services.elevenlabs_service import ElevenLabsService
from services.firebase_service import FirebaseService
from services.whisper_service import WhisperService
from services.emotion_service import EmotionService
from services.pronunciation_service import PronunciationService

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
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'storage/audio'
app.config['SESSION_FOLDER'] = 'storage/sessions'

# Initialize services
groq_service = GroqService()
claude_service = ClaudeService()
elevenlabs_service = ElevenLabsService()
firebase_service = FirebaseService()
whisper_service = WhisperService()
emotion_service = EmotionService()
pronunciation_service = PronunciationService()

# Ensure storage directories exist
Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
Path(app.config['SESSION_FOLDER']).mkdir(parents=True, exist_ok=True)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'HoloMentor AR',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'groq': groq_service.is_available(),
            'claude': claude_service.is_available(),
            'elevenlabs': elevenlabs_service.is_available(),
            'firebase': firebase_service.is_available(),
            'whisper': whisper_service.is_available()
        }
    })


@app.route('/api/user/create', methods=['POST'])
def create_user():
    """Create a new user profile"""
    try:
        data = request.json
        user_id = data.get('user_id', str(uuid.uuid4()))
        name = data.get('name', 'Student')
        age = data.get('age')
        learning_goals = data.get('learning_goals', [])
        
        user_profile = {
            'user_id': user_id,
            'name': name,
            'age': age,
            'learning_goals': learning_goals,
            'created_at': datetime.utcnow().isoformat(),
            'total_sessions': 0,
            'learning_progress': {},
            'emotional_trends': {
                'overall_mood': 'neutral',
                'engagement_score': 0.5,
                'confidence_level': 0.5
            },
            'preferences': {
                'voice_id': 'default',
                'avatar_style': 'friendly',
                'difficulty_level': 'beginner'
            }
        }
        
        # Store in Firebase
        firebase_service.create_user(user_id, user_profile)
        
        logger.info(f"Created user profile: {user_id}")
        return jsonify({
            'success': True,
            'user_id': user_id,
            'message': 'User profile created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    """Transcribe audio using Whisper"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        user_id = request.form.get('user_id', 'anonymous')
        
        # Save audio temporarily
        filename = f"{user_id}_{datetime.now().timestamp()}.webm"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(filepath)
        
        # Transcribe with Whisper
        transcription = whisper_service.transcribe(filepath)
        
        # Analyze pronunciation
        pronunciation_analysis = pronunciation_service.analyze(filepath, transcription['text'])
        
        # Detect emotion from speech
        emotion_analysis = emotion_service.analyze_audio(filepath)
        
        # Update user profile with emotion data
        if user_id != 'anonymous':
            firebase_service.update_emotion_trends(user_id, emotion_analysis)
        
        logger.info(f"Transcribed audio for user {user_id}: {transcription['text']}")
        
        return jsonify({
            'success': True,
            'transcription': transcription['text'],
            'confidence': transcription.get('confidence', 0.9),
            'pronunciation': pronunciation_analysis,
            'emotion': emotion_analysis,
            'audio_file': filename
        })
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ask', methods=['POST'])
def ask_question():
    """
    Fast real-time responses using Groq Llama 3 70B + ElevenLabs TTS
    For quick questions, conversational AI, instant feedback
    """
    try:
        data = request.json
        user_id = data.get('user_id', 'anonymous')
        question = data.get('question', '')
        context = data.get('context', {})
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Get user profile for personalization
        user_profile = None
        if user_id != 'anonymous':
            user_profile = firebase_service.get_user(user_id)
        
        # Build personalized context
        system_context = build_personalized_context(user_profile, context)
        
        # Get fast response from Groq Llama 3 70B
        logger.info(f"Processing question from {user_id}: {question}")
        response = groq_service.get_response(
            question=question,
            system_context=system_context,
            user_profile=user_profile
        )
        
        # Generate natural speech with ElevenLabs
        audio_response = elevenlabs_service.text_to_speech(
            text=response['answer'],
            voice_id=user_profile.get('preferences', {}).get('voice_id', 'default') if user_profile else 'default'
        )
        
        # Save interaction to Firebase
        if user_id != 'anonymous':
            firebase_service.log_interaction(
                user_id=user_id,
                interaction_type='question',
                question=question,
                response=response['answer'],
                context=context
            )
        
        logger.info(f"Generated response for {user_id}")
        
        return jsonify({
            'success': True,
            'answer': response['answer'],
            'audio_url': audio_response['audio_url'],
            'audio_duration': audio_response['duration'],
            'thinking_points': response.get('thinking_points', []),
            'follow_up_questions': response.get('follow_up_questions', []),
            'response_time': response.get('response_time', 0)
        })
        
    except Exception as e:
        logger.error(f"Error in /api/ask: {e}")
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
        plan_type = data.get('plan_type', 'lesson')  # lesson, quiz, curriculum
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
            plan['audio_intro_url'] = audio_intro['audio_url']
        
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


@app.route('/api/user/<user_id>/progress', methods=['GET'])
def get_user_progress(user_id):
    """Get user learning progress and trends"""
    try:
        user_profile = firebase_service.get_user(user_id)
        
        if not user_profile:
            return jsonify({'error': 'User not found'}), 404
        
        # Get detailed progress analytics
        progress_data = firebase_service.get_learning_progress(user_id)
        emotional_trends = firebase_service.get_emotion_trends(user_id)
        recent_interactions = firebase_service.get_recent_interactions(user_id, limit=10)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'name': user_profile.get('name'),
            'total_sessions': user_profile.get('total_sessions', 0),
            'learning_progress': progress_data,
            'emotional_trends': emotional_trends,
            'recent_interactions': recent_interactions,
            'recommendations': generate_recommendations(user_profile, progress_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting user progress: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/user/<user_id>/update', methods=['POST'])
def update_user_profile(user_id):
    """Update user profile and preferences"""
    try:
        data = request.json
        
        # Update user profile in Firebase
        firebase_service.update_user(user_id, data)
        
        logger.info(f"Updated user profile: {user_id}")
        return jsonify({
            'success': True,
            'message': 'User profile updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/unity/avatar/state', methods=['POST'])
def update_avatar_state():
    """
    Unity AR integration endpoint for avatar state management
    Handles avatar animations, gestures, and visual feedback
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        state = data.get('state')  # listening, thinking, speaking, idle
        metadata = data.get('metadata', {})
        
        # Log avatar state for analytics
        if user_id:
            firebase_service.log_avatar_interaction(user_id, state, metadata)
        
        return jsonify({
            'success': True,
            'state': state,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error updating avatar state: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/unity/session/start', methods=['POST'])
def start_ar_session():
    """Start a new AR learning session"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        # Create session in Firebase
        session_id = firebase_service.create_session(user_id)
        
        # Get user profile
        user_profile = firebase_service.get_user(user_id)
        
        # Get personalized greeting
        greeting = groq_service.generate_greeting(user_profile)
        
        # Generate greeting audio
        greeting_audio = elevenlabs_service.text_to_speech(
            text=greeting,
            voice_id=user_profile.get('preferences', {}).get('voice_id', 'default')
        )
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'greeting': greeting,
            'greeting_audio_url': greeting_audio['audio_url'],
            'user_name': user_profile.get('name'),
            'avatar_config': user_profile.get('preferences', {})
        })
        
    except Exception as e:
        logger.error(f"Error starting AR session: {e}")
        return jsonify({'error': str(e)}), 500


def build_personalized_context(user_profile, additional_context):
    """Build personalized context for AI responses"""
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
    
    context.update(additional_context)
    return context


def generate_recommendations(user_profile, progress_data):
    """Generate personalized learning recommendations"""
    recommendations = []
    
    # Analyze weak areas
    if progress_data:
        weak_topics = [topic for topic, score in progress_data.items() if score < 0.7]
        if weak_topics:
            recommendations.append({
                'type': 'review',
                'topics': weak_topics,
                'message': 'Consider reviewing these topics to strengthen understanding'
            })
    
    # Check engagement
    emotional_trends = user_profile.get('emotional_trends', {})
    if emotional_trends.get('engagement_score', 0.5) < 0.5:
        recommendations.append({
            'type': 'engagement',
            'message': 'Try interactive quizzes or gamified lessons to boost engagement'
        })
    
    return recommendations


if __name__ == '__main__':
    logger.info("🚀 Starting HoloMentor AR Server")
    logger.info(f"📡 Groq: {'✓' if groq_service.is_available() else '✗'}")
    logger.info(f"🤖 Claude: {'✓' if claude_service.is_available() else '✗'}")
    logger.info(f"🔊 ElevenLabs: {'✓' if elevenlabs_service.is_available() else '✗'}")
    logger.info(f"🔥 Firebase: {'✓' if firebase_service.is_available() else '✗'}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', 'False') == 'True')

