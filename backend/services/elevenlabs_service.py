"""
ElevenLabs Service - Text-to-Speech and Speech-to-Text
"""

import os
import logging
import uuid
import requests
from pathlib import Path
from elevenlabs import generate, set_api_key

logger = logging.getLogger(__name__)


class ElevenLabsService:
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        # Use path relative to backend directory
        backend_dir = Path(__file__).parent.parent
        self.output_dir = backend_dir / 'storage' / 'audio' / 'tts'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Simple voice mapping - Daniel for British Harry Potter feel
        self.voice_id = "0W0wYbNB1YlMLulZ1dH9"  # Daniel - British, deep, mature
        
        if self.api_key:
            set_api_key(self.api_key)
            logger.info("ElevenLabs service initialized with Daniel (British) voice")
        else:
            logger.warning("ElevenLabs API key not found")
            self.api_key = None
    
    def is_available(self):
        """Check if ElevenLabs service is available"""
        return self.api_key is not None
    
    def text_to_speech(self, text, voice_id=None, settings=None):
        """
        Convert text to speech using Daniel voice (British)
        Returns audio file path
        
        Args:
            text: Text to convert to speech
            voice_id: Optional voice ID (ignored, using fixed Daniel voice)
            settings: Optional voice settings (ignored)
        """
        if not self.api_key:
            raise Exception("ElevenLabs service not available")
        
        try:
            logger.info(f"Generating speech: {text[:50]}...")
            
            # Generate audio with Daniel voice (British, Harry Potter-like)
            audio = generate(
                text=text,
                voice=self.voice_id,
                model="eleven_flash_v2_5"  # Fast model
            )
            
            # Save audio file
            filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
            filepath = self.output_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(audio)
            
            logger.info(f"Generated audio: {filename}")
            
            return {
                'audio_url': f'/api/audio/tts/{filename}',
                'audio_path': str(filepath),
                'filename': filename
            }
            
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {e}")
            raise
    
    def speech_to_text(self, audio_path):
        """
        Convert speech to text using ElevenLabs STT API
        Returns transcription with metadata
        
        Args:
            audio_path: Path to audio file to transcribe
        """
        if not self.api_key:
            raise Exception("ElevenLabs service not available")
        
        try:
            logger.info(f"Transcribing audio with ElevenLabs STT: {audio_path}")
            
            # Check file extension to determine MIME type
            audio_ext = Path(audio_path).suffix.lower()
            mime_types = {
                '.wav': 'audio/wav',
                '.mp3': 'audio/mpeg',
                '.m4a': 'audio/mp4',
                '.ogg': 'audio/ogg',
                '.flac': 'audio/flac'
            }
            mime_type = mime_types.get(audio_ext, 'audio/wav')
            
            # ElevenLabs STT API endpoint
            url = "https://api.elevenlabs.io/v1/speech-to-text"
            
            headers = {
                "xi-api-key": self.api_key
            }
            
            # Read audio file
            with open(audio_path, 'rb') as audio_file:
                files = {
                    'audio': (os.path.basename(audio_path), audio_file, mime_type)
                }
                
                response = requests.post(url, headers=headers, files=files, timeout=30)
                
                # Check for errors and provide detailed error message
                if response.status_code == 422:
                    error_detail = response.text
                    logger.error(f"ElevenLabs STT 422 error: {error_detail}")
                    raise Exception(f"ElevenLabs STT request format error (422). This may mean STT is not available in your plan or the request format is incorrect. Details: {error_detail}")
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"Transcription complete: {result.get('text', '')[:50]}...")
                
                return {
                    'text': result.get('text', ''),
                    'confidence': result.get('confidence', 0.9),
                    'language': result.get('language', 'en')
                }
                
        except requests.exceptions.HTTPError as e:
            error_msg = f"ElevenLabs STT HTTP error: {e}"
            if hasattr(e.response, 'text'):
                error_msg += f" - {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"ElevenLabs STT error: {e}")
            raise