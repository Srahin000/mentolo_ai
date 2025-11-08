#!/usr/bin/env python3
"""
Complete HoloMentor Test Suite
Tests all features: Gemini AI, ElevenLabs TTS/STT, Snowflake, Emotion Detection
"""

import os
import sys
import json
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')
TEST_USER_ID = 'test_user_harry_potter'

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def test_health_check():
    """Test 1: Health Check"""
    print_header("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        print_success("Health check successful!")
        print(f"\nService Status:")
        print(f"  Service: {data.get('service', 'Unknown')}")
        print(f"  Status: {data.get('status', 'Unknown')}")
        print(f"  Version: {data.get('version', 'Unknown')}")
        
        print(f"\nServices Available:")
        services = data.get('services', {})
        for service, available in services.items():
            status = "✓" if available else "✗"
            color = Colors.GREEN if available else Colors.RED
            print(f"  {color}{status}{Colors.RESET} {service}")
        
        return True, data
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False, None

def test_ask_endpoint():
    """Test 2: Ask Endpoint with Harry Potter Voice"""
    print_header("TEST 2: Ask Endpoint (Harry Potter Voice)")
    
    test_questions = [
        "I love dinosaurs! Can you tell me about them?",
        "What makes rockets fly?",
        "I'm really into drawing. What should I learn next?"
    ]
    
    results = []
    
    for i, question in enumerate(test_questions, 1):
        print_info(f"Question {i}: {question}")
        
        try:
            payload = {
                "user_input": question,
                "user_id": TEST_USER_ID,
                "context": {}
            }
            
            start_time = time.time()
            response = requests.post(
                f"{API_BASE_URL}/api/ask",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            elapsed = time.time() - start_time
            
            data = response.json()
            
            print_success(f"Response received in {elapsed:.2f}s")
            print(f"  Text: {data.get('text', '')[:100]}...")
            print(f"  Emotion: {data.get('emotion', 'unknown')}")
            print(f"  Audio URL: {data.get('audio_url', 'N/A')}")
            print(f"  Response Time: {data.get('response_time', 0):.2f}s")
            print(f"  Audio Duration: {data.get('audio_duration', 0):.1f}s")
            
            # Verify audio file exists
            if data.get('audio_url'):
                audio_path = data['audio_url'].replace(f"{API_BASE_URL}/api/audio/tts/", "")
                full_path = Path("backend/storage/audio/tts") / audio_path
                if full_path.exists():
                    print_success(f"Audio file exists: {full_path}")
                else:
                    print_warning(f"Audio file not found: {full_path}")
            
            results.append({
                'question': question,
                'success': True,
                'response_time': elapsed,
                'emotion': data.get('emotion'),
                'has_audio': bool(data.get('audio_url'))
            })
            
        except Exception as e:
            print_error(f"Question {i} failed: {e}")
            results.append({
                'question': question,
                'success': False,
                'error': str(e)
            })
        
        print()  # Blank line between questions
    
    return results

def test_snowflake_logging():
    """Test 3: Verify Snowflake Logging"""
    print_header("TEST 3: Snowflake Logging Verification")
    
    try:
        # Make a test request
        payload = {
            "user_input": "Test question for Snowflake logging",
            "user_id": TEST_USER_ID,
            "context": {}
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/ask",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        interaction_id = data.get('interaction_id')
        session_id = data.get('session_id')
        
        print_success("Request completed")
        print(f"  Interaction ID: {interaction_id}")
        print(f"  Session ID: {session_id}")
        
        # Note: Actual Snowflake verification would require database access
        print_info("Note: Verify in Snowflake UI that interaction was logged")
        print_info(f"  User ID: {TEST_USER_ID}")
        print_info(f"  Interaction ID: {interaction_id}")
        
        return True
        
    except Exception as e:
        print_error(f"Snowflake logging test failed: {e}")
        return False

def test_dashboard_endpoint():
    """Test 4: Dashboard Endpoint"""
    print_header("TEST 4: Dashboard Endpoint")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/dashboard",
            headers={"X-User-ID": TEST_USER_ID},
            params={"days": 30},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Dashboard data retrieved")
            print(f"  User ID: {data.get('user_id', 'N/A')}")
            
            summary = data.get('summary', {})
            print(f"\n  Summary:")
            print(f"    Total Interactions: {summary.get('total_interactions', 0)}")
            print(f"    Active Days: {summary.get('active_days', 0)}")
            print(f"    Engagement Score: {summary.get('engagement_score', 0):.2f}")
            print(f"    Most Common Emotion: {summary.get('most_common_emotion', 'N/A')}")
            
            insights = data.get('ai_insights', [])
            if insights:
                print(f"\n  AI Insights:")
                for insight in insights[:3]:
                    print(f"    • {insight}")
            
            return True
        else:
            print_warning(f"Dashboard returned status {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_error(f"Dashboard test failed: {e}")
        return False

def test_user_profile():
    """Test 5: User Profile Management"""
    print_header("TEST 5: User Profile Management")
    
    try:
        # Create/Update profile
        profile_data = {
            "name": "Test User",
            "age": 10,
            "learning_goals": ["Dinosaurs", "Space", "Art"],
            "preferences": {
                "difficulty_level": "beginner",
                "voice_id": "harry_potter"
            }
        }
        
        response = requests.put(
            f"{API_BASE_URL}/api/user/profile",
            json=profile_data,
            headers={"X-User-ID": TEST_USER_ID, "Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        
        print_success("Profile updated")
        print(f"  Name: {profile_data['name']}")
        print(f"  Age: {profile_data['age']}")
        print(f"  Learning Goals: {', '.join(profile_data['learning_goals'])}")
        print(f"  Voice: {profile_data['preferences']['voice_id']}")
        
        # Get profile
        response = requests.get(
            f"{API_BASE_URL}/api/user/profile",
            headers={"X-User-ID": TEST_USER_ID},
            timeout=10
        )
        response.raise_for_status()
        profile = response.json()
        
        print_success("Profile retrieved")
        print(f"  Profile keys: {', '.join(profile.keys())}")
        
        return True
        
    except Exception as e:
        print_error(f"Profile test failed: {e}")
        return False

def test_voice_verification():
    """Test 6: Verify Harry Potter Voice is Used"""
    print_header("TEST 6: Voice Verification (Harry Potter)")
    
    try:
        # Import service directly to check voice
        sys.path.insert(0, 'backend')
        from services.elevenlabs_service import ElevenLabsService
        
        service = ElevenLabsService()
        
        if not service.is_available():
            print_error("ElevenLabs service not available")
            return False
        
        # Check voice profile
        harry_potter_id = service.voice_profiles.get('harry_potter')
        default_id = service.voice_profiles.get('default')
        
        print_info("Voice Configuration:")
        print(f"  Default voice ID: {default_id}")
        print(f"  Harry Potter voice ID: {harry_potter_id}")
        
        if harry_potter_id == 'rnnUCKXlolNpwqQwp2gT' and default_id == 'rnnUCKXlolNpwqQwp2gT':
            print_success("Harry Potter voice is configured correctly!")
            return True
        else:
            print_error("Harry Potter voice not configured correctly")
            return False
            
    except Exception as e:
        print_error(f"Voice verification failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     HoloMentor Complete Test Suite                        ║")
    print("║     Testing: Gemini, ElevenLabs, Snowflake, Dashboard     ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(Colors.RESET)
    
    print_info(f"Testing against: {API_BASE_URL}")
    print_info(f"Test User ID: {TEST_USER_ID}\n")
    
    results = {
        'health_check': False,
        'ask_endpoint': False,
        'snowflake_logging': False,
        'dashboard': False,
        'user_profile': False,
        'voice_verification': False
    }
    
    # Test 1: Health Check
    success, health_data = test_health_check()
    results['health_check'] = success
    
    if not success:
        print_error("Health check failed. Please ensure the server is running.")
        print_info("Start server with: cd backend && python app.py")
        return results
    
    # Test 2: Ask Endpoint
    ask_results = test_ask_endpoint()
    results['ask_endpoint'] = all(r.get('success', False) for r in ask_results)
    
    # Test 3: Snowflake Logging
    results['snowflake_logging'] = test_snowflake_logging()
    
    # Test 4: Dashboard
    results['dashboard'] = test_dashboard_endpoint()
    
    # Test 5: User Profile
    results['user_profile'] = test_user_profile()
    
    # Test 6: Voice Verification
    results['voice_verification'] = test_voice_verification()
    
    # Summary
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        color = Colors.GREEN if passed_test else Colors.RED
        print(f"  {color}{status}{Colors.RESET} {test_name.replace('_', ' ').title()}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.RESET}\n")
    
    if passed == total:
        print_success("All tests passed! 🎉")
    else:
        print_warning(f"{total - passed} test(s) failed. Check the output above for details.")
    
    return results

if __name__ == "__main__":
    try:
        results = run_all_tests()
        sys.exit(0 if all(results.values()) else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

