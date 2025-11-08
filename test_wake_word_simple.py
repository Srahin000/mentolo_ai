#!/usr/bin/env python3
"""
Simple Console Wake Word Detection Test
Prints "DETECTED" when "Harry Potter" wake word is detected from microphone
"""

import os
import sys
import platform
from pathlib import Path

# Try to load from .env file manually
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and 'PICOVOICE_ACCESS_KEY' in line and '=' in line:
                key, value = line.split('=', 1)
                # Remove quotes if present
                value = value.strip().strip('"').strip("'")
                os.environ[key.strip()] = value

try:
    from pvporcupine import Porcupine
    import pyaudio
except ImportError:
    print("❌ Missing dependencies!")
    print("Install with:")
    print("  cd backend && pip install pvporcupine pyaudio")
    print("Or:")
    print("  pip3 install pvporcupine pyaudio")
    print("\nNote: On Mac, you may need: brew install portaudio")
    sys.exit(1)

def main():
    print("\n" + "="*60)
    print("  Picovoice Wake Word Detection Test")
    print("  Say 'Harry Potter' to test")
    print("="*60 + "\n")
    
    access_key = os.getenv('PICOVOICE_ACCESS_KEY')
    if not access_key:
        print("❌ Set PICOVOICE_ACCESS_KEY in .env file")
        print("   Get it from: https://console.picovoice.ai/\n")
        sys.exit(1)
    
    # Check for native .ppn file (not WASM)
    # The WASM model won't work with Python SDK - need native model
    wasm_model_path = Path(__file__).parent / 'Harry-Potter_en_wasm_v3_0_0' / 'Harry-Potter_en_wasm_v3_0_0.ppn'
    
    # Look for native Python model in different locations
    # Option 1: Native model in a separate folder (Mac ARM64)
    native_model_path = Path(__file__).parent / 'Harry-Potter_en_mac_arm64_v3_0_0' / 'Harry-Potter_en_mac_arm64_v3_0_0.ppn'
    
    # Option 2: Native model in Mac folder (generic Mac)
    native_model_path2 = Path(__file__).parent / 'Harry-Potter_en_mac_v3_0_0' / 'Harry-Potter_en_mac_v3_0_0.ppn'
    
    # Option 3: Native model in same folder but different name
    native_model_path3 = Path(__file__).parent / 'Harry-Potter_en_wasm_v3_0_0' / 'Harry-Potter_en_mac_arm64_v3_0_0.ppn'
    
    # Option 4: Check for any .ppn file that's not WASM in any Harry-Potter folder
    native_model_path4 = None
    for folder in Path(__file__).parent.glob('Harry-Potter_*'):
        if folder.is_dir() and 'wasm' not in folder.name.lower():
            for ppn_file in folder.glob('*.ppn'):
                if 'wasm' not in ppn_file.name.lower():
                    native_model_path4 = ppn_file
                    break
            if native_model_path4:
                break
    
    # Try to find native model
    keyword_paths = None
    use_builtin = True
    
    for model_path in [native_model_path, native_model_path2, native_model_path3, native_model_path4]:
        if model_path and model_path.exists() and 'wasm' not in str(model_path).lower():
            keyword_paths = [str(model_path)]
            use_builtin = False
            print(f"✅ Native model found: {model_path.name}")
            break
    
    if use_builtin:
        if wasm_model_path.exists():
            print(f"⚠️  Note: {wasm_model_path.name} is a WASM model (for web/mobile)")
            print(f"   Python console test needs a native .ppn file")
            print(f"\n📥 To use 'Harry Potter' wake word:")
            print(f"   1. Go to https://console.picovoice.ai/")
            print(f"   2. Find your 'Harry Potter' wake word")
            print(f"   3. Download the native Python version:")
            print(f"      - For Mac ARM64: Download 'mac/arm64' version")
            print(f"      - For Mac x86_64: Download 'mac/x86_64' version")
            print(f"      - For Linux: Download 'linux' version")
            print(f"   4. Save it as: Harry-Potter_en_mac_arm64_v3_0_0/Harry-Potter_en_mac_arm64_v3_0_0.ppn")
            print(f"      (or in the same folder as the WASM model)")
        else:
            print(f"⚠️  Model not found")
        print(f"\n   Using built-in 'porcupine' keyword for testing\n")
    
    if use_builtin:
        print(f"✅ Using built-in keyword: 'porcupine'")
    
    print(f"✅ Initializing...\n")
    
    try:
        # Use pvporcupine.create() function (simpler API like in demos)
        # This automatically handles library/model paths and built-in keywords
        import pvporcupine
        
        if keyword_paths:
            # Try to use native .ppn file for Harry Potter
            try:
                porcupine = pvporcupine.create(
                    access_key=access_key,
                    keyword_paths=keyword_paths,
                    sensitivities=[0.5]
                )
                wake_word_name = "Harry Potter"
                print(f"✅ Initialized with 'Harry Potter' wake word!\n")
            except Exception as e:
                print(f"❌ Custom model failed: {e}")
                if 'wasm' in str(e).lower() or 'invalid' in str(e).lower():
                    print(f"   This appears to be a WASM model (for web/mobile)")
                    print(f"   Download the native Python version from Picovoice Console\n")
                print(f"   Falling back to built-in keyword\n")
                keyword_paths = None
        
        if not keyword_paths:
            # Use built-in keyword using create() function (like in Porcupine demos)
            # This is the proper way according to Porcupine documentation
            porcupine = pvporcupine.create(
                access_key=access_key,
                keywords=['porcupine'],  # Built-in keyword
                sensitivities=[0.5]
            )
            wake_word_name = "porcupine"
        
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )
        
        print(f"🎤 Listening... Say '{wake_word_name}'")
        print("   Press Ctrl+C to stop\n")
        
        try:
            while True:
                pcm = audio_stream.read(porcupine.frame_length)
                pcm = [int.from_bytes(pcm[i:i+2], byteorder='little', signed=True) 
                       for i in range(0, len(pcm), 2)]
                
                keyword_index = porcupine.process(pcm)
                
                if keyword_index >= 0:
                    print("\n" + "="*60)
                    print(" " * 20 + "DETECTED!")
                    print("="*60)
                    print(f"🎤 Wake word '{wake_word_name}' detected!")
                    print("="*60 + "\n")
        
        except KeyboardInterrupt:
            print("\n✅ Stopped")
        finally:
            audio_stream.stop_stream()
            audio_stream.close()
            pa.terminate()
            porcupine.delete()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

