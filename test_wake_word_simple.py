#!/usr/bin/env python
"""
Ultra-simple test to verify Porcupine is working
No dependencies except pvporcupine and pyaudio
"""

import sys
import struct
import os

# Set access key directly (replace with yours)
PICOVOICE_ACCESS_KEY = os.getenv('PICOVOICE_ACCESS_KEY', 'YOUR_KEY_HERE')
MODEL_PATH = "Harry-Potter_en_mac_v3_0_0/Harry-Potter_en_mac_v3_0_0.ppn"

try:
    import pvporcupine
    import pyaudio
except ImportError as e:
    print(f"Missing package: {e}")
    print("Install with: pip install pvporcupine pyaudio")
    sys.exit(1)

print("=" * 60)
print("SIMPLE WAKE WORD TEST")
print("=" * 60)
print(f"Model: {MODEL_PATH}")
print(f"Access key: {PICOVOICE_ACCESS_KEY[:10]}...")
print()

# Initialize Porcupine
try:
    porcupine = pvporcupine.create(
        access_key=PICOVOICE_ACCESS_KEY,
        keyword_paths=[MODEL_PATH]
    )
    print("✅ Porcupine initialized")
    print(f"   Sample rate: {porcupine.sample_rate} Hz")
    print(f"   Frame length: {porcupine.frame_length}")
except Exception as e:
    print(f"❌ Failed to initialize Porcupine: {e}")
    sys.exit(1)

# Open audio stream
try:
    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )
    print("✅ Audio stream opened")
except Exception as e:
    print(f"❌ Failed to open audio: {e}")
    porcupine.delete()
    sys.exit(1)

print()
print("🎤 LISTENING FOR 'HARRY POTTER'...")
print("Press Ctrl+C to stop")
print("=" * 60)
print()

frame_count = 0
try:
    while True:
        # Read audio
        pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        
        # Process
        keyword_index = porcupine.process(pcm)
        
        frame_count += 1
        
        # Show we're listening
        if frame_count % 1000 == 0:
            print(f"Processed {frame_count} frames...")
        
        # Detection!
        if keyword_index >= 0:
            print("\n" + "🎉" * 20)
            print("✅ WAKE WORD DETECTED!")
            print("🎉" * 20 + "\n")
            
except KeyboardInterrupt:
    print("\n\n👋 Stopped by user")
finally:
    stream.close()
    pa.terminate()
    porcupine.delete()
    print(f"Total frames processed: {frame_count}")

