#!/usr/bin/env python
"""
Voice Assistant with Picovoice Wake Word Detection
Uses Porcupine for "Harry Potter" wake word detection
Uses backend services directly (Gemini, ElevenLabs)
"""

import os
import sys
import time
import logging
import threading
import struct
from datetime import datetime
from pathlib import Path

# Add parent directory and backend directory to path to import backend services
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'backend'))

# Try to import required libraries
try:
    import pvporcupine
    import pyaudio
except ImportError:
    print("Error: pvporcupine or pyaudio not installed.")
    print("Install with: pip install pvporcupine pyaudio")
    sys.exit(1)

try:
    import speech_recognition as sr
except ImportError:
    print("Error: speech_recognition not installed. Install with: pip install SpeechRecognition")
    sys.exit(1)

try:
    import pygame
except ImportError:
    print("Warning: pygame not installed. Audio playback will be limited.")
    print("Install with: pip install pygame")
    pygame = None

# Import backend services (for fallback if API unavailable)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import requests for API calls
try:
    import requests
except ImportError:
    print("Error: requests not installed. Install with: pip install requests")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more verbose output
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
WAKE_WORD = "Harry Potter"  # Picovoice wake word
PICOVOICE_ACCESS_KEY = os.getenv('PICOVOICE_ACCESS_KEY')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:3001')
TEST_USER_ID = os.getenv('VOICE_ASSISTANT_USER_ID', 'voice_assistant_user')
AUDIO_OUTPUT_DIR = Path("storage/audio/responses")
AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DEBUG_DIR = Path("storage/audio/debug")
AUDIO_DEBUG_DIR.mkdir(parents=True, exist_ok=True)

class VoiceAssistant:
    def __init__(self):
        # Initialize Porcupine for wake word detection
        if not PICOVOICE_ACCESS_KEY:
            logger.error("PICOVOICE_ACCESS_KEY not found in environment variables.")
            logger.error("Get your access key from: https://console.picovoice.ai/")
            sys.exit(1)
        
        logger.info("Initializing Picovoice Porcupine...")
        try:
            # Determine platform for correct model file
            import platform
            system = platform.system().lower()
            machine = platform.machine().lower()
            
            # Map platform to Porcupine model naming
            # Note: Picovoice uses different naming conventions
            if system == 'darwin':  # macOS
                # Try both generic 'mac' and specific architecture
                platform_variants = ['mac', 'mac_arm64', 'mac_x86_64']
            elif system == 'linux':
                if 'arm' in machine or 'aarch' in machine:
                    platform_variants = ['linux_arm64', 'linux']
                else:
                    platform_variants = ['linux_x86_64', 'linux']
            elif system == 'windows':
                platform_variants = ['windows']
            else:
                platform_variants = ['linux_x86_64', 'linux']  # Default fallback
            
            logger.info(f"Detected platform: {system} {machine}")
            
            # Try to find platform-specific "Harry Potter" wake word model file
            # Check common locations with platform-specific naming
            model_paths = []
            
            # Add paths for each platform variant
            for variant in platform_variants:
                model_paths.extend([
                    Path(f"Harry-Potter_en_{variant}_v3_0_0/Harry-Potter_en_{variant}_v3_0_0.ppn"),
                    Path(f"../Harry-Potter_en_{variant}_v3_0_0/Harry-Potter_en_{variant}_v3_0_0.ppn"),
                ])
            
            # Also check common locations
            model_paths.extend([
                Path("Harry-Potter_en_wasm_v3_0_0/Harry-Potter_en_wasm_v3_0_0.ppn"),  # WASM (won't work but check anyway)
                Path("assets/Harry-Potter_en_wasm_v3_0_0.ppn"),  # WASM fallback
            ])
            
            keyword_path = None
            for path in model_paths:
                if path.exists():
                    # Check if it's WASM (won't work for Python)
                    if 'wasm' in str(path).lower():
                        logger.warning(f"Found WASM model (won't work for Python): {path}")
                        logger.warning("You need to download the platform-specific model for your OS")
                        continue
                    keyword_path = str(path.absolute())
                    logger.info(f"Found wake word model at: {keyword_path}")
                    break
            
            if keyword_path:
                # Use custom wake word model file
                logger.info(f"📁 Loading wake word model from: {keyword_path}")
                self.porcupine = pvporcupine.create(
                    access_key=PICOVOICE_ACCESS_KEY,
                    keyword_paths=[keyword_path]
                )
                logger.info("✅ Porcupine initialized with custom 'Harry Potter' wake word model")
                logger.info(f"   Model path: {keyword_path}")
                logger.info(f"   Sample rate: {self.porcupine.sample_rate} Hz")
                logger.info(f"   Frame length: {self.porcupine.frame_length}")
            else:
                # Try built-in keyword (if available)
                try:
                    self.porcupine = pvporcupine.create(
                        access_key=PICOVOICE_ACCESS_KEY,
                        keywords=["Harry-Potter"]
                    )
                    logger.info("✅ Porcupine initialized with built-in 'Harry Potter' keyword")
                except Exception as builtin_err:
                    # Fallback: provide clear instructions
                    logger.error("=" * 60)
                    logger.error("Harry Potter wake word model not found!")
                    logger.error("=" * 60)
                    logger.error(f"Platform detected: {system} {machine}")
                    logger.error(f"Tried platform variants: {', '.join(platform_variants)}")
                    logger.error("")
                    logger.error("To fix this:")
                    logger.error("1. Go to https://console.picovoice.ai/")
                    logger.error("2. Download the 'Harry Potter' wake word model")
                    logger.error(f"3. Select platform: {platform_variants[0]} (or compatible)")
                    logger.error(f"4. Place the .ppn file in the project directory")
                    logger.error(f"5. Expected path: Harry-Potter_en_{platform_variants[0]}_v3_0_0/Harry-Potter_en_{platform_variants[0]}_v3_0_0.ppn")
                    logger.error("")
                    logger.error("Note: The WASM model (Harry-Potter_en_wasm_v3_0_0.ppn) won't work")
                    logger.error("      You need the platform-specific model for Python")
                    raise Exception(f"Harry Potter wake word model not found for platform {platform_variants[0]}")
                    
        except Exception as e:
            logger.error(f"Failed to initialize Porcupine: {e}")
            logger.error("")
            logger.error("Troubleshooting:")
            logger.error("1. Verify PICOVOICE_ACCESS_KEY is valid")
            logger.error("2. Download the correct platform-specific model from Picovoice Console")
            logger.error("3. Ensure the .ppn file matches your OS (not WASM)")
            sys.exit(1)
        
        # Initialize PyAudio for Porcupine
        logger.info("Initializing PyAudio stream for Porcupine...")
        self.porcupine_audio = pyaudio.PyAudio()
        self.porcupine_stream = self.porcupine_audio.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
            # Stream auto-starts - DON'T stop it later!
        )
        logger.info(f"✅ Porcupine audio stream started (rate: {self.porcupine.sample_rate} Hz)")
        logger.info("💡 Tip: Porcupine stream will run continuously - speech_recognition uses a separate stream")
        
        # Initialize speech recognition for input (but DON'T open microphone yet!)
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Create persistent HTTP session for faster API calls (connection pooling)
        self.session = requests.Session()
        self.session.headers.update({'Connection': 'keep-alive'})
        
        # Test API connection
        logger.info(f"Testing API connection to {API_BASE_URL}...")
        try:
            response = self.session.get(f"{API_BASE_URL}/api/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ API connection successful (using persistent connection)")
                self.use_api = True
            else:
                logger.warning(f"API returned status {response.status_code}, will use direct services")
                self.use_api = False
        except Exception as e:
            logger.warning(f"API not available ({e}), will use direct services as fallback")
            self.use_api = False
            # Import services for fallback
            from services.gemini_service import GeminiService
            from services.elevenlabs_service import ElevenLabsService
            self.gemini_service = GeminiService(use_pro_model=False)
            self.elevenlabs_service = ElevenLabsService()
        
        # DON'T adjust for ambient noise here - it conflicts with Porcupine's microphone!
        # We'll do it when we actually need speech_recognition (after wake word detected)
        logger.info("✅ Ready to listen!")
        
    def listen_for_wake_word(self):
        """Listen continuously for wake word using Porcupine"""
        logger.info(f"🎤 Listening for wake word: '{WAKE_WORD}' (using Picovoice)...")
        logger.info(f"💡 Say '{WAKE_WORD}' clearly to activate")
        
        frame_count = 0
        last_status_time = time.time()
        
        try:
            while True:
                # Read audio frame from Porcupine stream
                pcm = self.porcupine_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                
                # Debug: Check audio levels every 50 frames
                if frame_count % 50 == 0 and frame_count > 0:
                    # Calculate audio level (RMS)
                    import math
                    rms = math.sqrt(sum(x*x for x in pcm) / len(pcm))
                    logger.debug(f"Audio level (RMS): {rms:.2f} - Frames: {frame_count}")
                
                # Process with Porcupine
                keyword_index = self.porcupine.process(pcm)
                
                frame_count += 1
                
                # Log status every 5 seconds to show it's working
                current_time = time.time()
                if current_time - last_status_time >= 5.0:
                    logger.info(f"🔄 Still listening... (processed {frame_count} frames) - Say '{WAKE_WORD}'")
                    last_status_time = current_time
                
                if keyword_index >= 0:
                    logger.info("")
                    logger.info("🎉" * 20)
                    logger.info(f"✅ Wake word '{WAKE_WORD}' detected!")
                    logger.info("🎉" * 20)
                    logger.info("")
                    return True
                    
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(f"Error in wake word detection: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def listen_for_input(self, timeout=5, validate_speech=False):
        """Listen for user input after wake word - temporarily close Porcupine stream
        
        Args:
            timeout: How long to wait for speech
            validate_speech: If True, validate with Google Speech Recognition (slower, more accurate)
        """
        logger.info("🎤 Listening for your input...")
        
        # Temporarily close Porcupine stream to free microphone
        logger.debug("Temporarily closing Porcupine stream...")
        try:
            self.porcupine_stream.stop_stream()
            self.porcupine_stream.close()
        except Exception as e:
            logger.debug(f"Error closing Porcupine stream: {e}")
        
        # Small delay to ensure microphone is released
        time.sleep(0.2)
        
        try:
            # Create a fresh recognizer instance to avoid conflicts
            temp_recognizer = sr.Recognizer()
            
            # Use speech_recognition's Microphone (now microphone is free)
            with sr.Microphone() as mic:
                # Adjust for ambient noise - quick adjustment
                logger.info("Adjusting for ambient noise...")
                temp_recognizer.adjust_for_ambient_noise(mic, duration=0.3)
                
                # Increase energy threshold to reduce false positives for follow-ups
                if validate_speech:
                    temp_recognizer.energy_threshold = max(temp_recognizer.energy_threshold, 500)
                
                # Listen for input with better settings
                logger.info("🎤 Speak your question now (I'm listening)...")
                # Shorter phrase limit for faster responses
                audio = temp_recognizer.listen(
                    mic, 
                    timeout=timeout,
                    phrase_time_limit=8,  # Reduced from 15 to 8 seconds
                )
                logger.info("✅ Audio captured, processing...")
            
            # Optional validation: Only for follow-ups to prevent false triggers
            if validate_speech:
                logger.debug("Validating speech...")
                try:
                    # Try to recognize to validate it's speech
                    test_text = temp_recognizer.recognize_google(audio, show_all=False)
                    if not test_text or len(test_text.strip()) < 3:
                        logger.info("⚠️  No clear speech detected (too short or empty)")
                        return None
                    logger.info(f"✓ Speech validated: '{test_text[:50]}...'")
                except sr.UnknownValueError:
                    logger.info("⚠️  Could not understand audio (likely background noise)")
                    return None
                except sr.RequestError as e:
                    logger.error(f"Speech recognition service error: {e}")
                    return None
                except Exception as e:
                    logger.warning(f"Speech validation error: {e}")
                    return None
            
            # Save audio file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_file = AUDIO_DEBUG_DIR / f"input_{timestamp}.wav"
            
            try:
                # Save the raw audio data
                audio_data = audio.get_wav_data()
                
                # Check minimum audio size (reject very short/empty audio)
                if len(audio_data) < 10000:  # Less than ~10KB is likely just noise
                    logger.info(f"⚠️  Audio too short ({len(audio_data)} bytes), likely noise")
                    return None
                
                with open(audio_file, "wb") as f:
                    f.write(audio_data)
                
                logger.info(f"✅ Audio saved to {audio_file}")
                logger.info(f"   Audio length: {len(audio_data)} bytes")
            except Exception as save_err:
                logger.error(f"Could not save audio: {save_err}")
                return None
            
            # Return the audio file path instead of text
            # The generate_response method will handle sending it to Gemini
            return str(audio_file)
                
        except sr.WaitTimeoutError:
            logger.warning("No input detected within timeout")
            return None
        except Exception as e:
            logger.error(f"Error listening for input: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            # Reopen Porcupine stream
            logger.debug("Reopening Porcupine stream...")
            try:
                self.porcupine_stream = self.porcupine_audio.open(
                    rate=self.porcupine.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=self.porcupine.frame_length
                )
                logger.debug("✅ Porcupine stream reopened")
            except Exception as e:
                logger.error(f"Failed to reopen Porcupine stream: {e}")
                import traceback
                traceback.print_exc()
    
    def generate_response(self, user_input):
        """Generate response using /api/ask endpoint (or fallback to direct service)"""
        
        # Check if user_input is an audio file path
        is_audio_file = isinstance(user_input, str) and user_input.endswith('.wav')
        
        if is_audio_file:
            logger.info(f"🎵 Processing audio file: {user_input}")
        else:
            logger.info(f"🤖 Generating response for: {user_input}")
        
        if self.use_api:
            try:
                start_time = time.time()
                
                if is_audio_file:
                    # Send audio file directly to backend
                    logger.info("📤 Sending audio to backend (Gemini multimodal)...")
                    
                    with open(user_input, 'rb') as audio_file:
                        files = {
                            'audio': (os.path.basename(user_input), audio_file, 'audio/wav')
                        }
                        data = {
                            'user_id': TEST_USER_ID
                        }
                        
                        response = self.session.post(
                            f"{API_BASE_URL}/api/ask",
                            files=files,
                            data=data,
                            timeout=30
                        )
                else:
                    # Send text input
                    payload = {
                        "user_input": user_input,
                        "user_id": TEST_USER_ID,
                        "context": {}
                    }
                    
                    response = self.session.post(
                        f"{API_BASE_URL}/api/ask",
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=30
                    )
                
                response.raise_for_status()
                elapsed = time.time() - start_time
                
                data = response.json()
                
                # Handle response structure (check both 'text' and 'answer' fields)
                # The /api/ask endpoint returns 'text' field according to test file
                response_text = data.get('text') or data.get('answer', '')
                audio_url = data.get('audio_url') or data.get('full_audio_url', '')
                emotion = data.get('emotion', 'unknown')
                
                # If response_text is still empty, try to get it from nested structure
                if not response_text and 'response' in data:
                    response_text = data['response'].get('answer', '')
                
                logger.info(f"💬 Response received in {elapsed:.2f}s")
                logger.info(f"   Emotion: {emotion}")
                logger.info(f"   Audio URL: {audio_url}")
                logger.info(f"   Text: {response_text[:100]}...")
                
                # Download audio file if available
                audio_file = None
                if audio_url:
                    try:
                        # Construct full URL if relative
                        if audio_url.startswith('/'):
                            full_audio_url = f"{API_BASE_URL}{audio_url}"
                        else:
                            full_audio_url = audio_url
                        
                        # Download audio (using persistent session)
                        audio_response = self.session.get(full_audio_url, timeout=10)
                        audio_response.raise_for_status()
                        
                        # Save to output directory
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        audio_file = AUDIO_OUTPUT_DIR / f"response_{timestamp}.mp3"
                        with open(audio_file, 'wb') as f:
                            f.write(audio_response.content)
                        
                        logger.info(f"✅ Audio downloaded to: {audio_file}")
                    except Exception as e:
                        logger.warning(f"Could not download audio: {e}")
                
                return {
                    'text': response_text,
                    'audio_file': audio_file,
                    'emotion': emotion,
                    'response_time': elapsed
                }
                
            except Exception as e:
                logger.error(f"API request failed: {e}")
                logger.info("Falling back to direct service calls...")
                # Fall through to fallback
        
        # Fallback: Use services directly
        try:
            from services.gemini_service import GeminiService
            from services.elevenlabs_service import ElevenLabsService
            
            if not hasattr(self, 'gemini_service'):
                self.gemini_service = GeminiService(use_pro_model=False)
                self.elevenlabs_service = ElevenLabsService()
            
            SYSTEM_CONTEXT = {
                'role': 'You are Harry Potter, a magical guide and friend. You are patient, encouraging, and make learning fun with a touch of magic.',
                'personality': 'friendly, magical, and enthusiastic about teaching',
                'instruction': 'Keep responses very brief and conversational for voice - 2-3 sentences maximum. Be warm but concise.',
                'student_name': 'Tommy',
                'age': 10,
                'learning_goals': ['science', 'math', 'space exploration'],
                'difficulty_level': 'intermediate'
            }
            
            # Handle audio or text input
            if is_audio_file:
                logger.info(f"🎵 Processing audio with Gemini multimodal (direct)...")
                gemini_response = self.gemini_service.get_response_from_audio(
                    audio_path=user_input,
                    system_context=SYSTEM_CONTEXT,
                    user_profile=None
                )
            else:
                gemini_response = self.gemini_service.get_response(
                    question=user_input,
                    system_context=SYSTEM_CONTEXT,
                    user_profile=None
                )
            
            response_text = gemini_response.get('answer', '')
            logger.info(f"💬 Response: {response_text}")
            
            # Generate TTS
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_file = AUDIO_OUTPUT_DIR / f"response_{timestamp}.mp3"
            
            if self.elevenlabs_service.is_available():
                result = self.elevenlabs_service.text_to_speech(response_text)
                import shutil
                shutil.copy(result['audio_path'], audio_file)
            else:
                # Fallback to gTTS
                from gtts import gTTS
                tts = gTTS(text=response_text, lang='en', slow=False)
                tts.save(str(audio_file))
            
            return {
                'text': response_text,
                'audio_file': audio_file,
                'emotion': 'neutral',
                'response_time': gemini_response.get('response_time', 0)
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                'text': f"I'm sorry, I encountered an error: {str(e)}",
                'audio_file': None,
                'emotion': 'error',
                'response_time': 0
            }
    
    def play_audio(self, audio_file):
        """Play audio file"""
        if not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return
        
        if pygame:
            try:
                pygame.mixer.init()
                pygame.mixer.music.load(str(audio_file))
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                logger.info("✅ Audio playback complete")
            except Exception as e:
                logger.error(f"Error playing audio: {e}")
        else:
            logger.info(f"Audio file saved at: {audio_file} (pygame not available for playback)")
    
    def wait_for_more_input(self, wait_seconds=4):
        """Wait for additional input after initial response"""
        logger.info(f"⏳ Waiting {wait_seconds} seconds for more input...")
        
        # Temporarily close Porcupine stream to free microphone
        logger.debug("Temporarily closing Porcupine stream for follow-up...")
        try:
            self.porcupine_stream.stop_stream()
            self.porcupine_stream.close()
        except Exception as e:
            logger.debug(f"Error closing Porcupine stream: {e}")
        
        time.sleep(0.2)  # Small delay
        
        try:
            start_time = time.time()
            while time.time() - start_time < wait_seconds:
                try:
                    # Use separate recognizer instance
                    temp_recognizer = sr.Recognizer()
                    with sr.Microphone() as mic:
                        audio = temp_recognizer.listen(mic, timeout=0.5, phrase_time_limit=wait_seconds)
                    
                    try:
                        text = temp_recognizer.recognize_google(audio)
                        logger.info(f"📝 Additional input: {text}")
                        return text
                    except (sr.UnknownValueError, sr.WaitTimeoutError):
                        continue
                except Exception:
                    time.sleep(0.1)
                    continue
            
            logger.info("No additional input received")
            return None
        finally:
            # Reopen Porcupine stream
            logger.debug("Reopening Porcupine stream after follow-up wait...")
            try:
                self.porcupine_stream = self.porcupine_audio.open(
                    rate=self.porcupine.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=self.porcupine.frame_length
                )
                logger.debug("✅ Porcupine stream reopened after follow-up")
            except Exception as e:
                logger.error(f"Failed to reopen Porcupine stream after follow-up: {e}")
                import traceback
                traceback.print_exc()
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up resources...")
        if hasattr(self, 'porcupine_stream'):
            try:
                self.porcupine_stream.close()
            except:
                pass
        if hasattr(self, 'porcupine_audio'):
            try:
                self.porcupine_audio.terminate()
            except:
                pass
        if hasattr(self, 'porcupine'):
            try:
                self.porcupine.delete()
            except:
                pass
        if hasattr(self, 'session'):
            try:
                self.session.close()
                logger.info("✅ HTTP session closed")
            except:
                pass
    
    def run(self):
        """Main loop"""
        logger.info("🚀 Voice Assistant started!")
        logger.info(f"Wake word: '{WAKE_WORD}' (Picovoice Porcupine)")
        logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                # Step 1: Listen for wake word (Porcupine stream runs continuously)
                if self.listen_for_wake_word():
                    # Step 2: Listen for user input (separate stream)
                    user_input = self.listen_for_input()
                
                    if user_input:
                        # Step 3: Generate response (includes TTS via /api/ask)
                        response_data = self.generate_response(user_input)
                        
                        response_text = response_data.get('text', '')
                        audio_file = response_data.get('audio_file')
                        emotion = response_data.get('emotion', 'unknown')
                        
                        if response_text:
                            logger.info(f"💬 Response: {response_text}")
                            logger.info(f"   Emotion detected: {emotion}")
                        
                        if audio_file and isinstance(audio_file, Path) and audio_file.exists():
                            # Play the audio
                            self.play_audio(audio_file)
                        elif audio_file:
                            logger.warning(f"Audio file not found: {audio_file}")
                        
                        # Step 4: Listen for follow-up question (without saying wake word again)
                        logger.info("💬 You can ask a follow-up question now (4 sec timeout), or stay quiet...")
                        follow_up_input = self.listen_for_input(timeout=4, validate_speech=True)
                        
                        if follow_up_input:
                            logger.info(f"📝 Follow-up detected! Processing question...")
                            # Generate response for follow-up
                            follow_up_response = self.generate_response(follow_up_input)
                            follow_up_audio = follow_up_response.get('audio_file')
                            
                            if follow_up_response.get('text'):
                                logger.info(f"💬 Follow-up response: {follow_up_response.get('text')}")
                            
                            if follow_up_audio and isinstance(follow_up_audio, Path) and follow_up_audio.exists():
                                self.play_audio(follow_up_audio)
                        else:
                            logger.info("⏭️  No follow-up question detected")
                        
                        logger.info("🔄 Returning to wake word listening...\n")
                        
                        # Verify stream is active
                        if hasattr(self, 'porcupine_stream') and self.porcupine_stream.is_active():
                            logger.debug("✅ Porcupine stream is active and ready")
                        else:
                            logger.warning("⚠️  Porcupine stream may not be active!")
                    else:
                        logger.warning("No input detected, returning to wake word listening...\n")
                
        except KeyboardInterrupt:
            logger.info("\n👋 Voice Assistant stopped by user")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            raise
        finally:
            self.cleanup()

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()

