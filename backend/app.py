#!/usr/bin/env python3
"""
HoloMentor Mobile AR - Flask Backend
Modular AI voice assistant API for mobile (React Native) and future Unity integration
"""

import os
import json
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# Import custom modules
from services.gemini_service import GeminiService
from services.claude_service import ClaudeService
from services.elevenlabs_service import ElevenLabsService
from services.firebase_service import FirebaseService
# Whisper replaced with ElevenLabs STT
from services.emotion_service import EmotionService
from services.snowflake_service import SnowflakeService
from services.places_service import PlacesService
from services.interest_service import InterestService
from services.child_development_service import ChildDevelopmentService
from firebase_admin import firestore

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
# Use Flash for quick responses (frontend)
gemini_service = GeminiService(use_pro_model=False)
# Pro model is used internally by ChildDevelopmentService for analysis
claude_service = ClaudeService()
elevenlabs_service = ElevenLabsService()
firebase_service = FirebaseService()
# Whisper service removed - using ElevenLabs STT instead
emotion_service = EmotionService()
snowflake_service = SnowflakeService()
places_service = PlacesService()
interest_service = InterestService()
child_dev_service = ChildDevelopmentService()  # Uses Pro model internally

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
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'services': {
            'gemini': gemini_service.is_available(),
            'claude': claude_service.is_available(),
            'elevenlabs': elevenlabs_service.is_available(),
            'firebase': firebase_service.is_available(),
            'elevenlabs_stt': elevenlabs_service.is_available(),  # ElevenLabs handles both TTS and STT
            'snowflake': snowflake_service.is_available(),
            'places': places_service.is_available()
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
                'preferences': data.get('preferences', {}),
                'location': data.get('location', {})  # Add location support
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


@app.route('/api/recommendations/coaching-centers', methods=['GET'])
def get_coaching_centers():
    """
    Get coaching center recommendations based on user interests and location
    
    Headers:
    - X-User-ID: User identifier (required)
    
    Query Parameters:
    - radius: Search radius in meters (default: 10000 = 10km)
    
    Returns:
    {
        "success": true,
        "user_id": "user123",
        "detected_interests": ["karate", "swimming"],
        "location": {"city": "San Francisco", "state": "CA"},
        "recommendations": [
            {
                "name": "Karate Dojo",
                "address": "123 Main St",
                "rating": 4.8,
                "phone": "+1234567890",
                "website": "https://...",
                "matched_interest": "karate"
            }
        ],
        "total_found": 5
    }
    """
    try:
        user_id = request.headers.get('X-User-ID', request.args.get('user_id', 'anonymous'))
        
        if user_id == 'anonymous':
            return jsonify({
                'error': 'User ID required',
                'message': 'Please provide X-User-ID header or user_id query parameter'
            }), 400
        
        # Get user profile - try both Firebase and Snowflake
        user_profile = {}
        
        # Try Firebase first
        if firebase_service.is_available():
            user_profile = firebase_service.get_user_profile(user_id) or {}
        
        # If not found in Firebase, try Snowflake
        if not user_profile and snowflake_service.is_available():
            try:
                cursor = snowflake_service.conn.cursor()
                # Try to select with location_json, fallback to without it
                try:
                    cursor.execute("""
                        SELECT name, age, learning_goals, preferences_json, location_json
                        FROM user_profiles 
                        WHERE user_id = %s
                    """, (user_id,))
                except:
                    # location_json column doesn't exist, select without it
                    cursor.execute("""
                        SELECT name, age, learning_goals, preferences_json
                        FROM user_profiles 
                        WHERE user_id = %s
                    """, (user_id,))
                
                result = cursor.fetchone()
                if result:
                    import json
                    preferences = json.loads(result[3]) if result[3] else {}
                    # Get location from preferences (stored there as fallback)
                    location = preferences.get('location', {})
                    
                    user_profile = {
                        'name': result[0],
                        'age': result[1],
                        'learning_goals': json.loads(result[2]) if result[2] else [],
                        'preferences': preferences,
                        'location': location
                    }
                cursor.close()
            except Exception as e:
                logger.warning(f"Could not retrieve profile from Snowflake: {e}")
        
        # If still no profile, return error
        if not user_profile:
            return jsonify({'error': 'User not found', 'message': 'Please create a user profile first using /api/user/profile'}), 404
        
        # Get user location
        location = user_profile.get('location')
        if not location:
            return jsonify({
                'error': 'Location not set',
                'message': 'Please update your profile with location (city, state, country or lat, lng)'
            }), 400
        
        # Extract interests
        interests = interest_service.extract_interests_from_profile(user_profile)
        
        # Also check recent conversations
        if firebase_service.is_available():
            recent_conversations = firebase_service.get_recent_interactions(user_id, limit=20)
            conversation_interests = interest_service.extract_interests_from_conversations(recent_conversations)
            interests.extend(conversation_interests)
        
        # Remove duplicates
        interests = list(set(interests))
        
        if not interests:
            return jsonify({
                'success': True,
                'message': 'No interests detected. Update your learning goals or have more conversations!',
                'recommendations': [],
                'detected_interests': []
            })
        
        # Check if Places service is available
        if not places_service.is_available():
            return jsonify({
                'error': 'Places service not configured',
                'message': 'Google Places API key is required for location-based recommendations'
            }), 503
        
        # Get recommendations for each interest
        all_recommendations = []
        radius = int(request.args.get('radius', 10000))  # 10km default
        
        for interest in interests[:3]:  # Limit to top 3 interests
            try:
                places = places_service.search_by_category(interest, location, radius=radius)
                
                for place in places:
                    place['matched_interest'] = interest
                    all_recommendations.append(place)
            except Exception as e:
                logger.error(f"Error searching for {interest}: {e}")
                continue
        
        # Sort by rating (highest first)
        all_recommendations.sort(key=lambda x: (x.get('rating', 0) or 0), reverse=True)
        
        logger.info(f"Found {len(all_recommendations)} recommendations for user {user_id}")
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'detected_interests': interests,
            'location': location,
            'recommendations': all_recommendations[:10],  # Top 10
            'total_found': len(all_recommendations)
        })
        
    except Exception as e:
        logger.error(f"Error getting coaching centers: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze-session', methods=['POST'])
def analyze_session():
    """
    Analyze a voice conversation session for child development insights
    
    Request (multipart/form-data):
    - audio_file: Audio file (MP3, WAV, etc.)
    - child_age: Integer (required)
    - child_name: String (required)
    - session_context: JSON string (optional)
      {
        "duration_minutes": 3,
        "known_interests": ["trucks", "dinosaurs"]
      }
    
    Response:
    {
        "session_id": "abc123",
        "transcript": "...",
        "analysis": { ... },
        "timestamp": "2025-11-08T..."
    }
    """
    try:
        # Get form data
        child_age = request.form.get('child_age')
        child_name = request.form.get('child_name', 'Child')
        session_context_str = request.form.get('session_context', '{}')
        
        if not child_age:
            return jsonify({'error': 'child_age is required'}), 400
        
        try:
            child_age = int(child_age)
        except ValueError:
            return jsonify({'error': 'child_age must be an integer'}), 400
        
        # Parse session context
        try:
            session_context = json.loads(session_context_str) if session_context_str else {}
        except json.JSONDecodeError:
            session_context = {}
        
        # Get audio file
        if 'audio_file' not in request.files:
            return jsonify({'error': 'audio_file is required'}), 400
        
        audio_file = request.files['audio_file']
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file provided'}), 400
        
        # Save audio temporarily
        session_id = str(uuid.uuid4())
        audio_filename = f"session_{session_id}.mp3"
        audio_path = Path(app.config['UPLOAD_FOLDER']) / audio_filename
        audio_file.save(audio_path)
        
        # Transcribe with ElevenLabs STT
        logger.info(f"Transcribing session {session_id} for {child_name} (age {child_age})")
        try:
            transcription = elevenlabs_service.speech_to_text(str(audio_path))
            transcript = transcription['text']
            
            if not transcript or len(transcript.strip()) < 10:
                return jsonify({
                    'error': 'Transcription too short or empty',
                    'message': 'Please ensure audio contains clear speech'
                }), 400
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return jsonify({'error': f'Transcription failed: {str(e)}'}), 500
        
        # Analyze with Gemini
        logger.info(f"Analyzing session {session_id} with Gemini")
        try:
            analysis = child_dev_service.analyze_session(
                transcript=transcript,
                child_age=child_age,
                child_name=child_name,
                session_context=session_context
            )
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
        
        # Store in Firebase
        user_id = request.headers.get('X-User-ID', request.form.get('user_id', 'anonymous'))
        
        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'child_name': child_name,
            'child_age': child_age,
            'transcript': transcript,
            'analysis': analysis,
            'audio_path': str(audio_path),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'session_context': session_context
        }
        
        if firebase_service.is_available():
            try:
                firebase_service.db.collection('child_sessions').document(session_id).set(session_data)
                
                # Update child profile
                profile_ref = firebase_service.db.collection('child_profiles').document(user_id)
                profile_ref.set({
                    'child_name': child_name,
                    'child_age': child_age,
                    'last_session': datetime.now(timezone.utc).isoformat(),
                    'total_sessions': firestore.Increment(1) if hasattr(firestore, 'Increment') else 1
                }, merge=True)
                
                logger.info(f"Saved session {session_id} to Firebase")
            except Exception as e:
                logger.warning(f"Failed to save to Firebase: {e}")
        
        # Store in Snowflake
        if snowflake_service.is_available():
            try:
                snowflake_service.save_child_development_session(session_data)
                logger.info(f"Saved session {session_id} to Snowflake")
            except Exception as e:
                logger.warning(f"Failed to save to Snowflake: {e}")
        
        return jsonify({
            'session_id': session_id,
            'transcript': transcript,
            'analysis': analysis,
            'timestamp': session_data['timestamp']
        })
        
    except Exception as e:
        logger.error(f"Error in /api/analyze-session: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/child-profile/<child_id>', methods=['GET'])
def get_child_profile(child_id):
    """
    Get aggregated child profile with longitudinal analysis
    
    Response:
    {
        "child_id": "...",
        "profile": { ... },
        "sessions": [ ... ],
        "trends": {
            "vocabulary_growth": [...],
            "complexity_progression": [...],
            "consistency": 0.85
        }
    }
    """
    try:
        # Get from Firebase
        sessions_list = []
        profile = {}
        
        if firebase_service.is_available():
            # Get all sessions
            sessions_ref = firebase_service.db.collection('child_sessions')
            sessions = sessions_ref.where('user_id', '==', child_id).order_by('timestamp').stream()
            sessions_list = [s.to_dict() for s in sessions]
            
            # Get profile
            profile_ref = firebase_service.db.collection('child_profiles').document(child_id)
            profile_doc = profile_ref.get()
            if profile_doc.exists:
                profile = profile_doc.to_dict()
        
        # Get trends from Snowflake (if available)
        trends = {}
        if snowflake_service.is_available():
            trends = snowflake_service.get_child_longitudinal_analysis(child_id)
        else:
            # Calculate basic trends from Firebase data
            if sessions_list:
                vocab_sizes = []
                complexities = []
                for session in sessions_list:
                    analysis = session.get('analysis', {})
                    vocab = analysis.get('vocabulary_analysis', {})
                    if vocab:
                        vocab_sizes.append(vocab.get('vocabulary_size_estimate', 0))
                        complexities.append(vocab.get('sentence_complexity', 0))
                
                trends = {
                    'vocabulary_growth': vocab_sizes,
                    'complexity_progression': complexities,
                    'consistency': len(sessions_list) / 30.0,  # sessions per month
                    'timeline': []
                }
        
        return jsonify({
            'child_id': child_id,
            'profile': profile,
            'sessions': sessions_list,
            'trends': trends,
            'total_sessions': len(sessions_list)
        })
        
    except Exception as e:
        logger.error(f"Error in /api/child-profile: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/adaptive-learning/<child_id>', methods=['GET'])
def get_adaptive_learning(child_id):
    """
    Get personalized activities based on child's interests and learning style
    
    Response:
    {
        "interests": ["trucks", "dinosaurs"],
        "known_concepts": ["colors", "counting"],
        "learning_style": "visual|kinesthetic|auditory",
        "personalized_activities": [ ... ]
    }
    """
    try:
        # Get past sessions from Firebase
        sessions_list = []
        if firebase_service.is_available():
            sessions_ref = firebase_service.db.collection('child_sessions')
            sessions = sessions_ref.where('user_id', '==', child_id).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(10).stream()
            sessions_list = [s.to_dict() for s in sessions]
        
        if not sessions_list:
            return jsonify({
                'interests': [],
                'known_concepts': [],
                'learning_style': 'unknown',
                'personalized_activities': []
            })
        
        # Extract interests and concepts
        interests = _extract_interests(sessions_list)
        known_concepts = _extract_known_concepts(sessions_list)
        learning_style = _detect_learning_style(sessions_list)
        
        # Generate personalized activities using Gemini
        activities_prompt = f"""Based on this child's interests: {', '.join(interests) if interests else 'general play'} and known concepts: {', '.join(known_concepts) if known_concepts else 'basic concepts'}, generate 5 personalized learning activities that bridge their interests to new learning.

Return JSON array of activities:
[
  {{
    "title": "Activity name",
    "description": "Brief description",
    "materials": ["item1", "item2"],
    "instructions": "Step-by-step",
    "learning_goals": ["goal1", "goal2"],
    "age_appropriate": true
  }}
]"""
        
        try:
            response = gemini_service.get_response(
                question=activities_prompt,
                system_context={'role': 'Educational Activity Designer'},
                user_profile=None
            )
            
            # Parse activities
            activities_text = response['answer']
            if '```json' in activities_text:
                json_start = activities_text.find('```json') + 7
                json_end = activities_text.find('```', json_start)
                activities_text = activities_text[json_start:json_end].strip()
            elif '[' in activities_text and ']' in activities_text:
                start = activities_text.find('[')
                end = activities_text.rfind(']') + 1
                activities_text = activities_text[start:end]
            
            activities = json.loads(activities_text)
        except Exception as e:
            logger.error(f"Error generating activities: {e}")
            activities = []
        
        return jsonify({
            'interests': interests,
            'known_concepts': known_concepts,
            'learning_style': learning_style,
            'personalized_activities': activities
        })
        
    except Exception as e:
        logger.error(f"Error in /api/adaptive-learning: {e}")
        return jsonify({'error': str(e)}), 500


def _extract_interests(sessions: List[Dict]) -> List[str]:
    """Extract child's interests from session analyses"""
    interests = set()
    for session in sessions:
        analysis = session.get('analysis', {})
        activities = analysis.get('personalized_activities', [])
        for activity in activities:
            activity_interests = activity.get('based_on_interests', [])
            if isinstance(activity_interests, list):
                interests.update(activity_interests)
    return list(interests)[:10]


def _extract_known_concepts(sessions: List[Dict]) -> List[str]:
    """Extract mastered concepts"""
    concepts = set()
    for session in sessions:
        analysis = session.get('analysis', {})
        milestones = analysis.get('milestone_progress', {})
        if isinstance(milestones, dict):
            concepts.update(milestones.get('on_track', []))
            concepts.update(milestones.get('ahead', []))
    return list(concepts)


def _detect_learning_style(sessions: List[Dict]) -> str:
    """Detect learning style from conversation patterns"""
    visual_keywords = ['see', 'look', 'picture', 'color', 'watch']
    kinesthetic_keywords = ['touch', 'feel', 'move', 'play', 'build', 'make']
    auditory_keywords = ['hear', 'sound', 'listen', 'say', 'sing', 'music']
    
    visual_count = 0
    kinesthetic_count = 0
    auditory_count = 0
    
    for session in sessions:
        transcript = session.get('transcript', '').lower()
        visual_count += sum(1 for kw in visual_keywords if kw in transcript)
        kinesthetic_count += sum(1 for kw in kinesthetic_keywords if kw in transcript)
        auditory_count += sum(1 for kw in auditory_keywords if kw in transcript)
    
    if visual_count > kinesthetic_count and visual_count > auditory_count:
        return 'visual'
    elif kinesthetic_count > auditory_count:
        return 'kinesthetic'
    else:
        return 'auditory'


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
    logger.info(f"🎤 ElevenLabs STT: {'✓' if elevenlabs_service.is_available() else '✗'}")
    logger.info(f"❄️  Snowflake: {'✓' if snowflake_service.is_available() else '✗'}")
    logger.info(f"📍 Google Places: {'✓' if places_service.is_available() else '✗'}")
    
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')  # Allow connections from mobile devices on same network
    
    logger.info(f"🌐 Server starting on http://{host}:{port}")
    logger.info(f"📱 Mobile app can connect at: http://YOUR_IP:{port}")
    
    app.run(host=host, port=port, debug=os.environ.get('DEBUG', 'False') == 'True')

