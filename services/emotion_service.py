"""
Emotion Detection Service - Analyze emotional state from speech and text
"""

import logging
import librosa
import numpy as np

logger = logging.getLogger(__name__)


class EmotionService:
    def __init__(self):
        """Initialize emotion detection service"""
        logger.info("Emotion service initialized")
    
    def analyze_audio(self, audio_path: str):
        """
        Analyze emotional content from audio
        Returns emotion classification and metrics
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=16000)
            
            # Extract acoustic features
            features = self._extract_features(y, sr)
            
            # Analyze emotion (simplified heuristic approach)
            # In production, use a proper emotion recognition model
            emotion_scores = self._analyze_features(features)
            
            return {
                'primary_emotion': emotion_scores['primary'],
                'confidence': emotion_scores['confidence'],
                'valence': emotion_scores['valence'],  # Positive/negative
                'arousal': emotion_scores['arousal'],  # Energy level
                'all_scores': emotion_scores['all_emotions']
            }
            
        except Exception as e:
            logger.error(f"Emotion analysis error: {e}")
            # Return neutral emotion on error
            return {
                'primary_emotion': 'neutral',
                'confidence': 0.5,
                'valence': 0.5,
                'arousal': 0.5,
                'all_scores': {}
            }
    
    def analyze_text(self, text: str):
        """
        Analyze emotional content from text
        Uses sentiment analysis and keyword detection
        """
        try:
            # Simple keyword-based analysis
            # In production, use NLP models like BERT for sentiment
            
            positive_words = ['happy', 'excited', 'love', 'great', 'wonderful', 'amazing', 'good']
            negative_words = ['sad', 'angry', 'hate', 'terrible', 'awful', 'bad', 'frustrated']
            confused_words = ['confused', 'lost', 'don\'t understand', 'unclear', 'what']
            
            text_lower = text.lower()
            
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            confused_count = sum(1 for word in confused_words if word in text_lower)
            
            # Determine primary emotion
            if confused_count > 0:
                primary = 'confused'
                valence = 0.4
            elif positive_count > negative_count:
                primary = 'positive'
                valence = 0.7
            elif negative_count > positive_count:
                primary = 'frustrated'
                valence = 0.3
            else:
                primary = 'neutral'
                valence = 0.5
            
            return {
                'primary_emotion': primary,
                'confidence': 0.7,
                'valence': valence,
                'arousal': 0.5,
                'sentiment_scores': {
                    'positive': positive_count,
                    'negative': negative_count,
                    'confused': confused_count
                }
            }
            
        except Exception as e:
            logger.error(f"Text emotion analysis error: {e}")
            return {
                'primary_emotion': 'neutral',
                'confidence': 0.5,
                'valence': 0.5,
                'arousal': 0.5
            }
    
    def _extract_features(self, y, sr):
        """Extract acoustic features from audio"""
        try:
            # Energy/Volume
            rms = librosa.feature.rms(y=y)[0]
            energy = np.mean(rms)
            
            # Pitch
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_mean = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 0
            
            # Tempo
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            
            # Spectral features
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
            
            # Zero crossing rate (indicator of noisiness/excitement)
            zcr = np.mean(librosa.feature.zero_crossing_rate(y))
            
            return {
                'energy': float(energy),
                'pitch': float(pitch_mean),
                'tempo': float(tempo),
                'spectral_centroid': float(spectral_centroid),
                'spectral_rolloff': float(spectral_rolloff),
                'zcr': float(zcr)
            }
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            return {
                'energy': 0.5,
                'pitch': 200,
                'tempo': 120,
                'spectral_centroid': 2000,
                'spectral_rolloff': 4000,
                'zcr': 0.05
            }
    
    def _analyze_features(self, features):
        """Analyze features to determine emotion"""
        # Simplified rule-based emotion detection
        # In production, use ML model trained on emotion datasets
        
        energy = features['energy']
        pitch = features['pitch']
        tempo = features['tempo']
        zcr = features['zcr']
        
        # High energy, high pitch, high tempo = excited/happy
        # Low energy, low pitch, slow tempo = sad/tired
        # High zcr, variable pitch = frustrated/angry
        # Moderate everything = neutral/calm
        
        # Normalize features (rough normalization)
        energy_norm = min(1.0, energy * 10)  # Scale energy
        pitch_norm = min(1.0, pitch / 500)   # Normalize pitch
        tempo_norm = min(1.0, tempo / 200)   # Normalize tempo
        zcr_norm = min(1.0, zcr * 20)        # Scale ZCR
        
        # Calculate arousal (energy level)
        arousal = (energy_norm + tempo_norm + zcr_norm) / 3
        
        # Calculate valence (positive/negative)
        valence = (pitch_norm + (1 - zcr_norm)) / 2
        
        # Determine primary emotion
        if arousal > 0.7 and valence > 0.6:
            primary = 'excited'
        elif arousal > 0.6 and valence < 0.4:
            primary = 'frustrated'
        elif arousal < 0.4 and valence < 0.4:
            primary = 'sad'
        elif arousal < 0.4 and valence > 0.6:
            primary = 'calm'
        else:
            primary = 'neutral'
        
        return {
            'primary': primary,
            'confidence': 0.75,
            'valence': float(valence),
            'arousal': float(arousal),
            'all_emotions': {
                'excited': float(arousal * valence),
                'frustrated': float(arousal * (1 - valence)),
                'calm': float((1 - arousal) * valence),
                'sad': float((1 - arousal) * (1 - valence)),
                'neutral': float(1 - abs(arousal - 0.5) - abs(valence - 0.5))
            }
        }

