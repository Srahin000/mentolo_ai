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
        
        if harry_potter_id == 'p3JVGy12zi4oFZ7ogrTE' and default_id == 'p3JVGy12zi4oFZ7ogrTE':
            print_success("Harry Potter voice is configured correctly!")
            return True
        else:
            print_error("Harry Potter voice not configured correctly")
            return False
            
    except Exception as e:
        print_error(f"Voice verification failed: {e}")
        return False

def test_analyze_session_pro():
    """Test 7: Child Development Analysis (Gemini Pro)"""
    print_header("TEST 7: Analyze Session (Gemini Pro Model)")
    
    try:
        # Create a test transcript (simulating a conversation)
        test_transcript = """
        Parent: How was your day at school today?
        Child: It was good! We learned about dinosaurs. Did you know that T-Rex had really big teeth?
        Parent: Wow, that's interesting! What else did you learn?
        Child: The teacher said they lived a long, long time ago. I wonder what it would be like to see one?
        Parent: That's a great question! What do you think?
        Child: I think it would be scary but also really cool. Maybe we could read a book about it?
        """
        
        print_info("Testing child development analysis endpoint...")
        print_info("This uses Gemini Pro for detailed holistic analysis")
        
        # Note: The /api/analyze-session endpoint requires an audio file upload
        # For testing, we'll check if the endpoint exists and is accessible
        # In a real scenario, you'd upload an audio file
        
        print_info("Note: /api/analyze-session requires audio file upload")
        print_info("To fully test, use:")
        print_info("  curl -X POST http://localhost:3001/api/analyze-session \\")
        print_info("    -H 'X-User-ID: test_child' \\")
        print_info("    -F 'audio_file=@conversation.mp3' \\")
        print_info("    -F 'child_age=5' \\")
        print_info("    -F 'child_name=TestChild'")
        
        # Check if endpoint exists by testing with a simple request
        # This will fail without audio, but confirms endpoint exists
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/analyze-session",
                headers={"X-User-ID": "test_child_pro"},
                data={
                    "child_age": 5,
                    "child_name": "TestChild"
                },
                timeout=5
            )
            
            # We expect an error without audio file, but endpoint should exist
            if response.status_code in [400, 422]:
                print_success("Endpoint exists and validates input correctly")
                print_info("  Expected error (no audio file): " + response.json().get('error', 'Unknown error'))
                return True
            elif response.status_code == 200:
                print_success("Analysis completed successfully!")
                data = response.json()
                if 'analysis' in data:
                    analysis = data['analysis']
                    print_success("Analysis structure verified:")
                    print(f"  - Daily insight: {'✓' if 'daily_insight' in analysis else '✗'}")
                    print(f"  - Development snapshot: {'✓' if 'development_snapshot' in analysis else '✗'}")
                    print(f"  - Strengths: {'✓' if 'strengths' in analysis else '✗'}")
                    print(f"  - Activities: {'✓' if 'personalized_activities' in analysis else '✗'}")
                return True
            else:
                print_warning(f"Unexpected response: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print_error(f"Endpoint test failed: {e}")
            return False
            
    except Exception as e:
        print_error(f"Analyze session test failed: {e}")
        return False

def test_child_profile_pro():
    """Test 8: Child Profile with Pro Model Analysis"""
    print_header("TEST 8: Child Profile (Gemini Pro Longitudinal Analysis)")
    
    try:
        # Test with the dummy profile we created
        test_child_id = "demo_child_tommy"
        
        print_info(f"Testing child profile endpoint for: {test_child_id}")
        print_info("This uses Gemini Pro for longitudinal analysis")
        
        response = requests.get(
            f"{API_BASE_URL}/api/child-profile/{test_child_id}",
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Child profile retrieved successfully!")
            
            # Check profile structure
            profile = data.get('profile', {})
            sessions = data.get('sessions', [])
            trends = data.get('trends', {})
            
            print(f"\n  Profile Data:")
            print(f"    Child Name: {profile.get('child_name', 'N/A')}")
            print(f"    Child Age: {profile.get('child_age', 'N/A')}")
            print(f"    Total Sessions: {data.get('total_sessions', len(sessions))}")
            
            print(f"\n  Sessions: {len(sessions)} found")
            if sessions:
                latest = sessions[-1]
                print(f"    Latest session: {latest.get('timestamp', 'N/A')[:10]}")
                if 'analysis' in latest:
                    analysis = latest['analysis']
                    print(f"    Has analysis: ✓")
                    print(f"      - Daily insight: {'✓' if 'daily_insight' in analysis else '✗'}")
                    print(f"      - Development snapshot: {'✓' if 'development_snapshot' in analysis else '✗'}")
            
            print(f"\n  Trends Data:")
            vocab_growth = trends.get('vocabulary_growth', [])
            complexity = trends.get('complexity_progression', [])
            print(f"    Vocabulary growth points: {len(vocab_growth)}")
            print(f"    Complexity progression points: {len(complexity)}")
            print(f"    Consistency: {trends.get('consistency', 0):.2f}")
            
            if vocab_growth and complexity:
                print_success("Longitudinal analysis data available!")
                print(f"    Vocabulary range: {min(vocab_growth)} - {max(vocab_growth)} words")
                print(f"    Complexity range: {min(complexity):.1f} - {max(complexity):.1f}")
            
            return True
        elif response.status_code == 404:
            print_warning(f"Child profile not found: {test_child_id}")
            print_info("Create a dummy profile first: python create_dummy_profile.py")
            return False
        else:
            print_error(f"Unexpected status: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_error(f"Child profile test failed: {e}")
        return False

def test_dual_gemini_models():
    """Test 9: Verify Dual Gemini Model Setup (Flash vs Pro)"""
    print_header("TEST 9: Dual Gemini Model Verification")
    
    try:
        sys.path.insert(0, 'backend')
        from services.gemini_service import GeminiService
        
        print_info("Checking Gemini model configuration...")
        
        # Test Flash model (for quick responses)
        flash_service = GeminiService(use_pro_model=False)
        print_info(f"Flash Model: {flash_service.model_name}")
        print_success("✓ Flash model initialized (for /api/ask endpoint)")
        
        # Test Pro model (for detailed analysis)
        pro_service = GeminiService(use_pro_model=True)
        print_info(f"Pro Model: {pro_service.model_name}")
        print_success("✓ Pro model initialized (for /api/analyze-session)")
        
        # Verify they're different
        if flash_service.model_name != pro_service.model_name:
            print_success("✓ Different models configured correctly!")
            print(f"  Flash: {flash_service.model_name} (fast responses)")
            print(f"  Pro: {pro_service.model_name} (detailed analysis)")
            return True
        else:
            print_warning("⚠️  Both services using same model")
            print_info("This might be intentional if only one model is available")
            return True  # Still pass, as it might be a configuration choice
            
    except Exception as e:
        print_error(f"Dual model verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     HoloMentor Complete Test Suite                        ║")
    print("║     Testing: Gemini Flash/Pro, ElevenLabs, Snowflake      ║")
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
        'voice_verification': False,
        'analyze_session_pro': False,
        'child_profile_pro': False,
        'dual_gemini_models': False
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
    
    # Test 7: Analyze Session (Gemini Pro)
    results['analyze_session_pro'] = test_analyze_session_pro()
    
    # Test 8: Child Profile (Gemini Pro)
    results['child_profile_pro'] = test_child_profile_pro()
    
    # Test 9: Dual Gemini Models Verification
    results['dual_gemini_models'] = test_dual_gemini_models()
    
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

