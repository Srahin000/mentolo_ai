#!/usr/bin/env python3
"""
Verification Script for HoloMentor Implementation
Checks that all services, imports, and dependencies are correctly configured
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def check_file_structure():
    """Check that all required files exist"""
    print_header("1. File Structure Check")
    
    required_files = [
        'backend/app.py',
        'backend/requirements.txt',
        'backend/services/__init__.py',
        'backend/services/gemini_service.py',
        'backend/services/claude_service.py',
        'backend/services/elevenlabs_service.py',
        'backend/services/firebase_service.py',
        'backend/services/emotion_service.py',
        'backend/services/snowflake_service.py',
        'backend/services/places_service.py',
        'backend/services/interest_service.py',
        'env.example',
        'mobile/config.js',
        'mobile/PicovoiceWakeWord.js',
        'mobile/ARPlaceholder.js',
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"{file_path}")
        else:
            print_error(f"{file_path} - MISSING")
            missing_files.append(file_path)
    
    # Check for deleted root requirements.txt (should NOT exist)
    if Path('requirements.txt').exists():
        print_warning("Root requirements.txt exists (should be deleted - using backend/requirements.txt)")
    else:
        print_success("Root requirements.txt correctly removed")
    
    return len(missing_files) == 0

def check_python_imports():
    """Check that all Python imports work"""
    print_header("2. Python Imports Check")
    
    print_info("Checking if dependencies are installed...")
    print_info("(If imports fail, install with: cd backend && pip install -r requirements.txt)\n")
    
    all_imported = True
    
    try:
        from services.gemini_service import GeminiService
        print_success("GeminiService")
    except ImportError as e:
        print_warning(f"GeminiService: {e}")
        print_info("  → Install: pip install google-generativeai")
        all_imported = False
    except Exception as e:
        print_error(f"GeminiService: {e}")
        all_imported = False
    
    try:
        from services.claude_service import ClaudeService
        print_success("ClaudeService")
    except ImportError as e:
        print_warning(f"ClaudeService: {e}")
        print_info("  → Install: pip install anthropic")
        all_imported = False
    except Exception as e:
        print_error(f"ClaudeService: {e}")
        all_imported = False
    
    try:
        from services.elevenlabs_service import ElevenLabsService
        print_success("ElevenLabsService")
    except ImportError as e:
        print_warning(f"ElevenLabsService: {e}")
        print_info("  → Install: pip install elevenlabs")
        all_imported = False
    except Exception as e:
        print_error(f"ElevenLabsService: {e}")
        all_imported = False
    
    try:
        from services.firebase_service import FirebaseService
        print_success("FirebaseService")
    except ImportError as e:
        print_warning(f"FirebaseService: {e}")
        print_info("  → Install: pip install firebase-admin")
        all_imported = False
    except Exception as e:
        print_error(f"FirebaseService: {e}")
        all_imported = False
    
    try:
        from services.emotion_service import EmotionService
        print_success("EmotionService")
    except Exception as e:
        print_warning(f"EmotionService: {e}")
        all_imported = False
    
    try:
        from services.snowflake_service import SnowflakeService
        print_success("SnowflakeService")
    except ImportError as e:
        print_warning(f"SnowflakeService: {e}")
        print_info("  → Install: pip install snowflake-connector-python")
        all_imported = False
    except Exception as e:
        print_error(f"SnowflakeService: {e}")
        all_imported = False
    
    try:
        from services.places_service import PlacesService
        print_success("PlacesService")
    except Exception as e:
        print_warning(f"PlacesService: {e}")
        all_imported = False
    
    try:
        from services.interest_service import InterestService
        print_success("InterestService")
    except Exception as e:
        print_warning(f"InterestService: {e}")
        all_imported = False
    
    if not all_imported:
        print_info("\n💡 Tip: Install all dependencies with:")
        print_info("   cd backend && pip install -r requirements.txt")
    
    return all_imported

def check_service_initialization():
    """Check that services can be initialized"""
    print_header("3. Service Initialization Check")
    
    try:
        from services.gemini_service import GeminiService
        gemini = GeminiService()
        print_success(f"GeminiService initialized (available: {gemini.is_available()})")
    except Exception as e:
        print_error(f"GeminiService initialization failed: {e}")
        return False
    
    try:
        from services.claude_service import ClaudeService
        claude = ClaudeService()
        print_success(f"ClaudeService initialized (available: {claude.is_available()})")
    except Exception as e:
        print_error(f"ClaudeService initialization failed: {e}")
        return False
    
    try:
        from services.elevenlabs_service import ElevenLabsService
        elevenlabs = ElevenLabsService()
        print_success(f"ElevenLabsService initialized (available: {elevenlabs.is_available()})")
        # Check Harry Potter voice configuration
        if 'harry_potter' in elevenlabs.voice_profiles:
            print_success("Harry Potter voice configured")
        else:
            print_warning("Harry Potter voice not in voice_profiles")
    except Exception as e:
        print_error(f"ElevenLabsService initialization failed: {e}")
        return False
    
    try:
        from services.firebase_service import FirebaseService
        firebase = FirebaseService()
        print_success(f"FirebaseService initialized (available: {firebase.is_available()})")
    except Exception as e:
        print_error(f"FirebaseService initialization failed: {e}")
        return False
    
    try:
        from services.emotion_service import EmotionService
        emotion = EmotionService()
        print_success("EmotionService initialized")
    except Exception as e:
        print_error(f"EmotionService initialization failed: {e}")
        return False
    
    try:
        from services.snowflake_service import SnowflakeService
        snowflake = SnowflakeService()
        print_success(f"SnowflakeService initialized (available: {snowflake.is_available()})")
    except Exception as e:
        print_error(f"SnowflakeService initialization failed: {e}")
        return False
    
    try:
        from services.places_service import PlacesService
        places = PlacesService()
        print_success(f"PlacesService initialized (available: {places.is_available()})")
    except Exception as e:
        print_error(f"PlacesService initialization failed: {e}")
        return False
    
    try:
        from services.interest_service import InterestService
        interest = InterestService()
        print_success("InterestService initialized")
    except Exception as e:
        print_error(f"InterestService initialization failed: {e}")
        return False
    
    return True

def check_backend_app():
    """Check that backend app.py can be imported"""
    print_header("4. Backend App Check")
    
    try:
        # Change to backend directory to import app
        original_dir = os.getcwd()
        os.chdir(backend_path)
        
        # Import app (this will initialize all services)
        import app
        
        print_success("Backend app.py imported successfully")
        print_info(f"Flask app: {app.app}")
        print_info(f"Services initialized: {len([s for s in dir(app) if '_service' in s])} services")
        
        os.chdir(original_dir)
        return True
    except Exception as e:
        print_error(f"Backend app.py import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_requirements_txt():
    """Check requirements.txt has all needed dependencies"""
    print_header("5. Requirements.txt Check")
    
    req_file = backend_path / 'requirements.txt'
    if not req_file.exists():
        print_error("backend/requirements.txt not found")
        return False
    
    with open(req_file) as f:
        content = f.read()
    
    required_packages = [
        'flask',
        'flask-cors',
        'python-dotenv',
        'google-generativeai',
        'anthropic',
        'elevenlabs',
        'firebase-admin',
        'snowflake-connector-python',
        'requests',
    ]
    
    missing_packages = []
    for package in required_packages:
        if package in content:
            print_success(f"{package}")
        else:
            print_warning(f"{package} not found in requirements.txt")
            missing_packages.append(package)
    
    # Check for groq (should be present)
    if 'groq' in content:
        print_success("groq (optional)")
    else:
        print_warning("groq not in requirements.txt (optional, but GroqService exists)")
    
    # Check for picovoice dependencies
    if 'pvporcupine' in content:
        print_success("pvporcupine (for wake word testing)")
    else:
        print_warning("pvporcupine not in requirements.txt")
    
    return True

def check_elevenlabs_stt():
    """Check that ElevenLabs STT method exists"""
    print_header("6. ElevenLabs STT Check")
    
    try:
        from services.elevenlabs_service import ElevenLabsService
        service = ElevenLabsService()
        
        if hasattr(service, 'speech_to_text'):
            print_success("speech_to_text method exists")
            return True
        else:
            print_error("speech_to_text method not found")
            return False
    except Exception as e:
        print_error(f"ElevenLabs STT check failed: {e}")
        return False

def check_firebase_methods():
    """Check that new Firebase methods exist"""
    print_header("7. Firebase Service Methods Check")
    
    try:
        from services.firebase_service import FirebaseService
        service = FirebaseService()
        
        required_methods = [
            'get_user_profile',
            'update_user_profile',
            'get_user_interactions',
        ]
        
        all_exist = True
        for method in required_methods:
            if hasattr(service, method):
                print_success(f"{method}()")
            else:
                print_error(f"{method}() not found")
                all_exist = False
        
        return all_exist
    except Exception as e:
        print_error(f"Firebase methods check failed: {e}")
        return False

def check_test_files():
    """Check that test files are configured correctly"""
    print_header("8. Test Files Check")
    
    test_voice = Path('test_voice_pipeline.py')
    test_complete = Path('test_holomentor_complete.py')
    
    if test_voice.exists():
        with open(test_voice) as f:
            content = f.read()
            if 'backend/requirements.txt' in content or 'cd backend' in content:
                print_success("test_voice_pipeline.py references backend/requirements.txt")
            else:
                print_warning("test_voice_pipeline.py may need updating")
    
    if test_complete.exists():
        with open(test_complete) as f:
            content = f.read()
            # Check API URL
            if 'localhost:3001' in content:
                print_warning("test_holomentor_complete.py uses port 3001 (should be 5000)")
            elif 'localhost:5000' in content:
                print_success("test_holomentor_complete.py uses correct port 5000")
            else:
                print_info("test_holomentor_complete.py API URL needs verification")
    
    return True

def main():
    print("\n" + "="*60)
    print("  HoloMentor Implementation Verification")
    print("  Checking merge compatibility and setup")
    print("="*60)
    
    results = {
        'file_structure': check_file_structure(),
        'python_imports': check_python_imports(),
        'service_initialization': check_service_initialization(),
        'backend_app': check_backend_app(),
        'requirements_txt': check_requirements_txt(),
        'elevenlabs_stt': check_elevenlabs_stt(),
        'firebase_methods': check_firebase_methods(),
        'test_files': check_test_files(),
    }
    
    print_header("Verification Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check_name, passed_check in results.items():
        status = "✅ PASS" if passed_check else "❌ FAIL"
        print(f"  {status} {check_name.replace('_', ' ').title()}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} checks passed")
    print(f"{'='*60}\n")
    
    if passed == total:
        print_success("All checks passed! Implementation is ready.")
        print_info("Next steps:")
        print_info("  1. Install dependencies: cd backend && pip install -r requirements.txt")
        print_info("  2. Create .env file with API keys")
        print_info("  3. Start backend: cd backend && python app.py")
        print_info("  4. Run tests: python test_voice_pipeline.py")
    else:
        print_warning(f"{total - passed} check(s) failed. Review the output above.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

