#!/usr/bin/env python3
"""
Child Development API Verification Test
Tests all child development endpoints and services
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

# Colors for output
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
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def test_health_check(base_url):
    """Test health check endpoint"""
    print_header("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        print_success("Health check passed")
        print_info(f"Service: {data.get('service', 'Unknown')}")
        print_info(f"Version: {data.get('version', 'Unknown')}")
        
        services = data.get('services', {})
        print(f"\n{Colors.BOLD}Service Status:{Colors.RESET}")
        for service, status in services.items():
            status_icon = "✓" if status else "✗"
            status_color = Colors.GREEN if status else Colors.RED
            print(f"  {status_color}{status_icon}{Colors.RESET} {service}")
        
        # Check required services
        required = ['gemini', 'elevenlabs']
        missing = [s for s in required if not services.get(s, False)]
        
        if missing:
            print_warning(f"Missing required services: {', '.join(missing)}")
            return False
        
        return True
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False

def create_test_audio():
    """Create a simple test audio file (or find existing one)"""
    # Check for existing test audio files
    test_files = [
        'test_audio.mp3',
        'test_conversation.mp3',
        'sample_audio.mp3',
        'backend/storage/audio/tts/*.mp3'
    ]
    
    for pattern in test_files:
        if '*' in pattern:
            import glob
            files = glob.glob(pattern)
            if files:
                return files[0]
        else:
            if os.path.exists(pattern):
                return pattern
    
    print_warning("No test audio file found")
    print_info("To test /api/analyze-session, you need an audio file")
    print_info("Options:")
    print_info("  1. Record a short conversation (2-3 minutes)")
    print_info("  2. Use an existing audio file")
    print_info("  3. Skip audio test for now")
    
    return None

def test_analyze_session(base_url, audio_file, user_id):
    """Test analyze-session endpoint"""
    print_header("TEST 2: Analyze Session Endpoint")
    
    if not audio_file or not os.path.exists(audio_file):
        print_warning("Skipping analyze-session test (no audio file)")
        return None
    
    try:
        print_info(f"Uploading audio: {audio_file}")
        
        with open(audio_file, 'rb') as f:
            files = {'audio_file': (os.path.basename(audio_file), f, 'audio/mpeg')}
            data = {
                'child_age': '4',
                'child_name': 'TestChild',
                'session_context': json.dumps({
                    'duration_minutes': 2,
                    'known_interests': ['toys', 'play']
                })
            }
            headers = {'X-User-ID': user_id}
            
            print_info("Sending request to /api/analyze-session...")
            response = requests.post(
                f"{base_url}/api/analyze-session",
                files=files,
                data=data,
                headers=headers,
                timeout=60  # Analysis can take time
            )
        
        response.raise_for_status()
        result = response.json()
        
        print_success("Session analyzed successfully!")
        print_info(f"Session ID: {result.get('session_id', 'N/A')}")
        print_info(f"Transcript length: {len(result.get('transcript', ''))} characters")
        
        analysis = result.get('analysis', {})
        if analysis:
            print_success("Analysis received")
            
            # Check analysis structure
            required_fields = ['daily_insight', 'development_snapshot', 'strengths']
            for field in required_fields:
                if field in analysis:
                    print_success(f"  ✓ {field} present")
                else:
                    print_warning(f"  ✗ {field} missing")
            
            # Show daily insight
            insight = analysis.get('daily_insight', '')
            if insight:
                print(f"\n{Colors.BOLD}Daily Insight:{Colors.RESET}")
                print(f"  {insight[:100]}...")
            
            # Show development scores
            snapshot = analysis.get('development_snapshot', {})
            if snapshot:
                print(f"\n{Colors.BOLD}Development Scores:{Colors.RESET}")
                for area, data in snapshot.items():
                    if isinstance(data, dict):
                        score = data.get('score', 0)
                        level = data.get('level', 'unknown')
                        print(f"  {area.title()}: {score}/100 ({level})")
        
        return result.get('session_id')
    except requests.exceptions.Timeout:
        print_error("Request timed out (analysis taking too long)")
        return None
    except Exception as e:
        print_error(f"Analyze session failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                print_error(f"  Error: {error_data.get('error', 'Unknown error')}")
            except:
                print_error(f"  Status: {e.response.status_code}")
        return None

def test_child_profile(base_url, child_id):
    """Test child-profile endpoint"""
    print_header("TEST 3: Child Profile Endpoint")
    
    try:
        print_info(f"Fetching profile for: {child_id}")
        response = requests.get(
            f"{base_url}/api/child-profile/{child_id}",
            headers={'X-User-ID': child_id},
            timeout=10
        )
        
        response.raise_for_status()
        data = response.json()
        
        print_success("Child profile retrieved")
        print_info(f"Total sessions: {data.get('total_sessions', 0)}")
        
        profile = data.get('profile', {})
        if profile:
            print_success("Profile data found")
            print_info(f"  Child name: {profile.get('child_name', 'N/A')}")
            print_info(f"  Child age: {profile.get('child_age', 'N/A')}")
        
        trends = data.get('trends', {})
        if trends:
            print_success("Trends data found")
            vocab_growth = trends.get('vocabulary_growth', [])
            if vocab_growth:
                print_info(f"  Vocabulary data points: {len(vocab_growth)}")
                if len(vocab_growth) > 1:
                    growth = vocab_growth[-1] - vocab_growth[0]
                    print_info(f"  Vocabulary growth: {growth} words")
        
        return True
    except Exception as e:
        print_error(f"Child profile test failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                print_error(f"  Error: {error_data.get('error', 'Unknown error')}")
            except:
                pass
        return False

def test_adaptive_learning(base_url, child_id):
    """Test adaptive-learning endpoint"""
    print_header("TEST 4: Adaptive Learning Endpoint")
    
    try:
        print_info(f"Fetching adaptive learning for: {child_id}")
        response = requests.get(
            f"{base_url}/api/adaptive-learning/{child_id}",
            headers={'X-User-ID': child_id},
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        print_success("Adaptive learning data retrieved")
        
        interests = data.get('interests', [])
        if interests:
            print_success(f"Interests detected: {', '.join(interests[:5])}")
        else:
            print_warning("No interests detected (need more sessions)")
        
        learning_style = data.get('learning_style', 'unknown')
        print_info(f"Learning style: {learning_style}")
        
        activities = data.get('personalized_activities', [])
        if activities:
            print_success(f"Generated {len(activities)} personalized activities")
            print(f"\n{Colors.BOLD}Sample Activity:{Colors.RESET}")
            if activities:
                activity = activities[0]
                print(f"  Title: {activity.get('title', 'N/A')}")
                print(f"  Duration: {activity.get('duration', 'N/A')}")
                print(f"  Materials: {', '.join(activity.get('materials', []))}")
        else:
            print_warning("No activities generated (need more session data)")
        
        return True
    except Exception as e:
        print_error(f"Adaptive learning test failed: {e}")
        return False

def test_services_available():
    """Check if required services are configured"""
    print_header("TEST 0: Service Configuration Check")
    
    services = {
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'ELEVENLABS_API_KEY': os.getenv('ELEVENLABS_API_KEY'),
        'FIREBASE_CREDENTIALS_PATH': os.getenv('FIREBASE_CREDENTIALS_PATH'),
        'SNOWFLAKE_ACCOUNT': os.getenv('SNOWFLAKE_ACCOUNT'),
    }
    
    required = ['GEMINI_API_KEY', 'ELEVENLABS_API_KEY']
    optional = ['FIREBASE_CREDENTIALS_PATH', 'SNOWFLAKE_ACCOUNT']
    
    all_required = True
    for service in required:
        if services[service]:
            print_success(f"{service} configured")
        else:
            print_error(f"{service} NOT configured (required)")
            all_required = False
    
    for service in optional:
        if services[service]:
            print_success(f"{service} configured (optional)")
        else:
            print_warning(f"{service} not configured (optional)")
    
    # Check Firebase credentials file
    firebase_path = services.get('FIREBASE_CREDENTIALS_PATH')
    if firebase_path:
        if os.path.exists(firebase_path):
            print_success(f"Firebase credentials file exists: {firebase_path}")
        else:
            print_warning(f"Firebase credentials file not found: {firebase_path}")
    
    return all_required

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   Child Development API Verification Test                ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(Colors.RESET)
    
    # Get base URL
    base_url = os.getenv('API_BASE_URL', 'http://localhost:5000')
    print_info(f"Testing API at: {base_url}")
    
    # Test user ID
    test_user_id = 'test-parent-' + str(int(time.time()))
    
    results = {
        'services': False,
        'health': False,
        'analyze_session': None,
        'child_profile': False,
        'adaptive_learning': False
    }
    
    # Test 0: Service configuration
    results['services'] = test_services_available()
    
    if not results['services']:
        print_error("\n⚠️  Missing required API keys. Some tests will fail.")
        print_info("Configure API keys in .env file before testing")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Test 1: Health check
    results['health'] = test_health_check(base_url)
    
    if not results['health']:
        print_error("\n⚠️  Server health check failed. Is the server running?")
        print_info("Start server with: cd backend && python app.py")
        sys.exit(1)
    
    # Test 2: Analyze session
    audio_file = create_test_audio()
    session_id = test_analyze_session(base_url, audio_file, test_user_id)
    results['analyze_session'] = session_id is not None
    
    # Wait a bit for data to be stored
    if session_id:
        print_info("Waiting 2 seconds for data to be stored...")
        time.sleep(2)
    
    # Test 3: Child profile
    results['child_profile'] = test_child_profile(base_url, test_user_id)
    
    # Test 4: Adaptive learning
    results['adaptive_learning'] = test_adaptive_learning(base_url, test_user_id)
    
    # Summary
    print_header("Test Summary")
    
    total_tests = len([r for r in results.values() if isinstance(r, bool)])
    passed_tests = sum([1 for r in results.values() if r is True])
    
    print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
    print(f"  Services Config: {'✅' if results['services'] else '❌'}")
    print(f"  Health Check: {'✅' if results['health'] else '❌'}")
    print(f"  Analyze Session: {'✅' if results['analyze_session'] else '⚠️  (skipped)'}")
    print(f"  Child Profile: {'✅' if results['child_profile'] else '❌'}")
    print(f"  Adaptive Learning: {'✅' if results['adaptive_learning'] else '❌'}")
    
    print(f"\n{Colors.BOLD}Total: {passed_tests}/{total_tests} tests passed{Colors.RESET}")
    
    if passed_tests == total_tests:
        print_success("\n🎉 All tests passed! Child development system is working.")
    elif passed_tests >= total_tests - 1:
        print_warning("\n⚠️  Most tests passed. Check warnings above.")
    else:
        print_error("\n❌ Some tests failed. Check errors above.")
    
    print(f"\n{Colors.BOLD}Next Steps:{Colors.RESET}")
    print("  1. Ensure all API keys are configured in .env")
    print("  2. Start the Flask server: cd backend && python app.py")
    print("  3. Test with real audio file for full analysis")
    print("  4. Build React dashboard to visualize the data")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

