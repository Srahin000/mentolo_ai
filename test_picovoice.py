#!/usr/bin/env python3
"""
Simple test script to verify Picovoice Porcupine wake word detection
Tests if "Harry Potter" wake word can be detected
"""

import os
import sys
import struct
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import pvporcupine
    import pyaudio
except ImportError as e:
    print(f"Error: Required packages not installed: {e}")
    print("Install with: pip install pvporcupine pyaudio")
    sys.exit(1)

# Configuration
PICOVOICE_ACCESS_KEY = os.getenv('PICOVOICE_ACCESS_KEY')
WAKE_WORD = "Harry Potter"

def test_picovoice():
    """Test Picovoice wake word detection"""
    
    if not PICOVOICE_ACCESS_KEY:
        logger.error("PICOVOICE_ACCESS_KEY not found in environment variables.")
        logger.error("Get your access key from: https://console.picovoice.ai/")
        return False
    
    logger.info("=" * 60)
    logger.info("Picovoice Porcupine Wake Word Test")
    logger.info("=" * 60)
    logger.info(f"Wake word: '{WAKE_WORD}'")
    logger.info("")
    
    # Determine platform
    import platform
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == 'darwin':
        platform_variants = ['mac', 'mac_arm64', 'mac_x86_64']
    elif system == 'linux':
        if 'arm' in machine or 'aarch' in machine:
            platform_variants = ['linux_arm64', 'linux']
        else:
            platform_variants = ['linux_x86_64', 'linux']
    elif system == 'windows':
        platform_variants = ['windows']
    else:
        platform_variants = ['linux_x86_64', 'linux']
    
    logger.info(f"Platform: {system} {machine}")
    logger.info(f"Trying variants: {', '.join(platform_variants)}")
    logger.info("")
    
    # Find model file
    model_paths = []
    for variant in platform_variants:
        model_paths.extend([
            Path(f"Harry-Potter_en_{variant}_v3_0_0/Harry-Potter_en_{variant}_v3_0_0.ppn"),
            Path(f"../Harry-Potter_en_{variant}_v3_0_0/Harry-Potter_en_{variant}_v3_0_0.ppn"),
        ])
    
    keyword_path = None
    for path in model_paths:
        if path.exists() and 'wasm' not in str(path).lower():
            keyword_path = str(path.absolute())
            logger.info(f"✅ Found model: {keyword_path}")
            break
    
    if not keyword_path:
        logger.error("❌ Wake word model not found!")
        logger.error(f"Looked for: {[str(p) for p in model_paths[:3]]}")
        return False
    
    # Initialize Porcupine
    try:
        logger.info("Initializing Porcupine...")
        porcupine = pvporcupine.create(
            access_key=PICOVOICE_ACCESS_KEY,
            keyword_paths=[keyword_path]
        )
        logger.info("✅ Porcupine initialized successfully!")
        logger.info(f"   Sample rate: {porcupine.sample_rate} Hz")
        logger.info(f"   Frame length: {porcupine.frame_length}")
        logger.info("")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Porcupine: {e}")
        return False
    
    # Initialize audio stream
    try:
        logger.info("Initializing audio stream...")
        audio = pyaudio.PyAudio()
        stream = audio.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )
        logger.info("✅ Audio stream opened")
        logger.info("")
    except Exception as e:
        logger.error(f"❌ Failed to open audio stream: {e}")
        logger.error("Check microphone permissions and availability")
        porcupine.delete()
        return False
    
    # Test wake word detection
    logger.info("=" * 60)
    logger.info("🎤 LISTENING FOR WAKE WORD...")
    logger.info(f"Say '{WAKE_WORD}' to test detection")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    logger.info("")
    
    detection_count = 0
    try:
        while True:
            # Read audio frame
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            
            # Process with Porcupine
            keyword_index = porcupine.process(pcm)
            
            if keyword_index >= 0:
                detection_count += 1
                logger.info("")
                logger.info("🎉" * 20)
                logger.info(f"✅ WAKE WORD DETECTED! (#{detection_count})")
                logger.info(f"   Wake word: '{WAKE_WORD}'")
                logger.info("🎉" * 20)
                logger.info("")
                logger.info("Continuing to listen... (Press Ctrl+C to stop)")
                logger.info("")
                
    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 60)
        logger.info("Test stopped by user")
        logger.info("=" * 60)
        logger.info("")
        logger.info(f"Total detections: {detection_count}")
        
        if detection_count > 0:
            logger.info("✅ SUCCESS: Wake word detection is working!")
            return True
        else:
            logger.warning("⚠️  No wake words detected during test")
            logger.warning("   Make sure you said 'Harry Potter' clearly")
            logger.warning("   Check microphone volume and permissions")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during detection: {e}")
        return False
        
    finally:
        # Cleanup
        logger.info("Cleaning up...")
        try:
            stream.close()
            audio.terminate()
            porcupine.delete()
            logger.info("✅ Resources cleaned up")
        except:
            pass

if __name__ == "__main__":
    try:
        success = test_picovoice()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

