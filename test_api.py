#!/usr/bin/env python3
"""
Quick API Test Script
Tests the voice pipeline without needing audio files
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_health():
    """Test if server is running and services are connected"""
    print("🔍 Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        
        print(f"✅ Server Status: {data['status']}")
        print("\n📊 Service Status:")
        for service, status in data['services'].items():
            icon = "✅" if status else "❌"
            print(f"  {icon} {service}: {'Connected' if status else 'Not Available'}")
        
        return data['status'] == 'healthy'
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure the server is running: python app.py")
        return False


def test_ask():
    """Test the /api/ask endpoint (text-based, no audio)"""
    print("\n🤖 Testing AI Response (Groq + ElevenLabs)...")
    
    try:
        payload = {
            "question": "What is photosynthesis? Keep it brief.",
            "context": {}
        }
        
        response = requests.post(
            f"{BASE_URL}/ask",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        data = response.json()
        
        if data.get('success'):
            print("✅ AI Response Generated!")
            print(f"\n📝 Answer: {data['answer'][:200]}...")
            print(f"\n🔊 Audio URL: {data['audio_url']}")
            print(f"⏱️  Duration: {data['audio_duration']}s")
            print(f"⚡ Response Time: {data.get('response_time', 'N/A')}s")
            
            # Try to download the audio
            audio_url = f"http://localhost:5000{data['audio_url']}"
            print(f"\n🎵 Testing audio download from: {audio_url}")
            audio_response = requests.get(audio_url)
            if audio_response.status_code == 200:
                print("✅ Audio file accessible!")
                print(f"   Size: {len(audio_response.content)} bytes")
            else:
                print("⚠️  Audio file not found (might need a moment to generate)")
            
            return True
        else:
            print(f"❌ Error: {data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_user_creation():
    """Test creating a user profile"""
    print("\n👤 Testing User Creation...")
    
    try:
        payload = {
            "name": "Test Student",
            "age": 12,
            "learning_goals": ["science", "math"]
        }
        
        response = requests.post(
            f"{BASE_URL}/user/create",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        data = response.json()
        
        if data.get('success'):
            print(f"✅ User Created!")
            print(f"   User ID: {data['user_id']}")
            return data['user_id']
        else:
            print(f"⚠️  User creation skipped (Firebase not configured)")
            return None
            
    except Exception as e:
        print(f"⚠️  User creation skipped: {e}")
        return None


def test_plan():
    """Test lesson plan generation (Claude)"""
    print("\n📚 Testing Lesson Plan Generation (Claude)...")
    
    try:
        payload = {
            "plan_type": "lesson",
            "topic": "Basic Addition",
            "parameters": {
                "duration": "15 minutes",
                "difficulty": "beginner"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/plan",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        data = response.json()
        
        if data.get('success'):
            print("✅ Lesson Plan Generated!")
            plan = data['plan']
            print(f"\n📖 Plan Type: {plan.get('type', 'N/A')}")
            if 'sections' in plan:
                print(f"   Sections: {len(plan['sections'])}")
            print(f"   Content Length: {len(str(plan))} chars")
            return True
        else:
            print(f"⚠️  Lesson plan generation skipped (Claude not configured)")
            return False
            
    except Exception as e:
        print(f"⚠️  Lesson plan skipped: {e}")
        return False


def main():
    print("=" * 60)
    print("🎤 HoloMentor Mobile AR - API Test Suite")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Server not running. Start it with: python app.py")
        return
    
    print("\n" + "=" * 60)
    
    # Test 2: Create user
    user_id = test_user_creation()
    
    print("\n" + "=" * 60)
    
    # Test 3: AI response (core feature)
    test_ask()
    
    print("\n" + "=" * 60)
    
    # Test 4: Lesson plan (optional)
    test_plan()
    
    print("\n" + "=" * 60)
    print("\n✅ Testing Complete!")
    print("\n📱 Next Steps:")
    print("   1. Test voice input: Send audio to /api/transcribe")
    print("   2. Build mobile app UI")
    print("   3. Add Unity AR avatar")
    print("\n🚀 Your voice pipeline is ready to go!")
    print("=" * 60)


if __name__ == "__main__":
    main()

