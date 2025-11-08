"""
Whisper Service - Speech-to-Text Transcription
"""

import os
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)


class WhisperService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = None
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info("Whisper service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Whisper: {e}")
    
    def is_available(self):
        """Check if Whisper service is available"""
        return self.client is not None
    
    def transcribe(self, audio_path: str, language: str = 'en'):
        """
        Transcribe audio file using Whisper
        Returns transcription with metadata
        """
        if not self.client:
            raise Exception("Whisper service not available")
        
        try:
            logger.info(f"Transcribing audio: {audio_path}")
            
            with open(audio_path, 'rb') as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="verbose_json"
                )
            
            logger.info(f"Transcription complete: {transcription.text}")
            
            return {
                'text': transcription.text,
                'language': transcription.language,
                'duration': transcription.duration,
                'confidence': self._estimate_confidence(transcription)
            }
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise
    
    def _estimate_confidence(self, transcription):
        """Estimate confidence from Whisper output"""
        # Whisper doesn't provide direct confidence scores
        # Estimate based on text quality
        text = transcription.text
        
        if len(text) < 5:
            return 0.5
        
        # Simple heuristic: longer, well-formed text = higher confidence
        word_count = len(text.split())
        if word_count > 10:
            return 0.95
        elif word_count > 5:
            return 0.85
        else:
            return 0.75

