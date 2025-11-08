"""
ElevenLabs TTS Service - Natural, Expressive Voice Synthesis
"""

import os
import logging
import uuid
from pathlib import Path
from elevenlabs import generate, voices, Voice, VoiceSettings, set_api_key

logger = logging.getLogger(__name__)


class ElevenLabsService:
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        self.output_dir = Path('storage/audio/tts')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Voice mappings for different personas
        # Using voice IDs instead of names for better compatibility
        self.voice_profiles = {
            'default': '21m00Tcm4TlvDq8ikWAM',  # Rachel - Warm, clear female voice
            'friendly': 'TxGEqnHWrfWFTfGW9XjX',  # Josh - Friendly male voice
            'professional': 'EXAVITQu4vr4xnSDxMaL',  # Bella - Professional female voice
            'energetic': 'ErXwobaYiN019PkySvjV',  # Antoni - Energetic male voice
            'calm': 'MF3mGyEYCl7XYWbV9V6O'  # Elli - Calm, soothing female voice
        }
        
        # Cache available voices on first use
        self._available_voices = None
        
        if self.api_key:
            # Set API key for ElevenLabs SDK
            set_api_key(self.api_key)
            os.environ['ELEVENLABS_API_KEY'] = self.api_key
            logger.info("ElevenLabs service initialized")
        else:
            logger.warning("ElevenLabs API key not found")
            self.api_key = None
    
    def is_available(self):
        """Check if ElevenLabs service is available"""
        return self.api_key is not None
    
    def text_to_speech(self, text, voice_id='default', settings=None):
        """
        Convert text to natural speech using ElevenLabs
        Returns audio file path and metadata
        """
        if not self.api_key:
            raise Exception("ElevenLabs service not available")
        
        try:
            # Map voice_id to actual voice ID or name
            # First try to get available voices if not cached
            if self._available_voices is None and self.api_key:
                try:
                    from elevenlabs import voices
                    self._available_voices = {v.name: v.voice_id for v in voices()}
                    logger.info(f"Found {len(self._available_voices)} available voices")
                except:
                    self._available_voices = {}
            
            # Get voice - try voice ID first, then name
            voice_identifier = self.voice_profiles.get(voice_id, 'default')
            
            # If it's a name, try to find the voice ID
            if voice_identifier in self._available_voices:
                voice_identifier = self._available_voices[voice_identifier]
            
            voice_name = voice_identifier
            
            # Default voice settings for educational content
            if settings is None:
                settings = VoiceSettings(
                    stability=0.75,  # High stability for clear pronunciation
                    similarity_boost=0.80,  # Natural voice characteristics
                    style=0.5,  # Balanced expressiveness
                    use_speaker_boost=True
                )
            
            logger.info(f"Generating speech with voice: {voice_name}")
            
            # Generate audio using ElevenLabs API
            # Pass API key explicitly to ensure it's used
            audio = generate(
                text=text,
                voice=voice_name,
                model="eleven_multilingual_v2",
                api_key=self.api_key
            )
            
            # Save audio file
            filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
            filepath = self.output_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(audio)
            
            # Calculate approximate duration (rough estimate)
            # Average speaking rate: ~150 words per minute = 2.5 words per second
            word_count = len(text.split())
            duration = (word_count / 2.5)
            
            logger.info(f"Generated audio: {filename} ({duration:.1f}s)")
            
            return {
                'audio_url': f'/api/audio/tts/{filename}',
                'audio_path': str(filepath),
                'duration': duration,
                'voice': voice_name,
                'text': text,
                'filename': filename
            }
            
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {e}")
            raise
    
    def generate_with_emotion(self, text, emotion='neutral', voice_id='default'):
        """
        Generate speech with specific emotional tone
        Adjusts voice settings based on desired emotion
        """
        emotion_settings = {
            'excited': VoiceSettings(
                stability=0.65,
                similarity_boost=0.85,
                style=0.8,
                use_speaker_boost=True
            ),
            'calm': VoiceSettings(
                stability=0.85,
                similarity_boost=0.75,
                style=0.3,
                use_speaker_boost=True
            ),
            'encouraging': VoiceSettings(
                stability=0.70,
                similarity_boost=0.80,
                style=0.6,
                use_speaker_boost=True
            ),
            'neutral': VoiceSettings(
                stability=0.75,
                similarity_boost=0.80,
                style=0.5,
                use_speaker_boost=True
            )
        }
        
        settings = emotion_settings.get(emotion, emotion_settings['neutral'])
        return self.text_to_speech(text, voice_id, settings)
    
    def get_available_voices(self):
        """Get list of available voices"""
        if not self.api_key:
            return list(self.voice_profiles.keys())
        
        try:
            available_voices = voices()
            return [voice.name for voice in available_voices]
        except Exception as e:
            logger.error(f"Error fetching voices: {e}")
            return list(self.voice_profiles.keys())
    
    def clone_voice(self, name, audio_files):
        """
        Clone a voice from sample audio files
        Useful for creating custom tutor voices
        """
        if not self.api_key:
            raise Exception("ElevenLabs service not available")
        
        try:
            from elevenlabs import clone
            
            voice = clone(
                name=name,
                files=audio_files
            )
            
            logger.info(f"Voice cloned: {name}")
            return voice
            
        except Exception as e:
            logger.error(f"Voice cloning error: {e}")
            raise

