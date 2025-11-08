#!/usr/bin/env python3
"""
Quick Test Script for HoloMentor Voice Pipeline
Tests the /api/ask endpoint without needing mobile app
"""

import requests
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_backend_health():
    """Test if backend is running"""
    print("🔍 Testing backend health...")
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is running!")
            print(f"   Service: {data.get('service', 'Unknown')}")
            print("\n📊 Service Status:")
            services = data.get('services', {})
            for service, status in services.items():
                icon = "✅" if status else "❌"
                print(f"   {icon} {service}: {'Connected' if status else 'Not Available'}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend!")
        print("   Make sure backend is running: cd backend && python app.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ask_endpoint():
    """Test the /api/ask endpoint"""
    print("\n🤖 Testing /api/ask endpoint...")
    
    test_question = "What is photosynthesis? Keep it brief, one sentence."
    
    try:
        print(f"📝 Sending question: '{test_question}'")
        
        response = requests.post(
            "http://localhost:5000/api/ask",
            json={
                "user_input": test_question,
                "context": {}
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✅ Success! Response received:")
            print(f"\n📝 Text Response:")
            print(f"   {data.get('text', 'N/A')[:200]}...")
            
            print(f"\n🔊 Audio URL:")
            print(f"   {data.get('audio_url', 'N/A')}")
            
            print(f"\n😊 Detected Emotion:")
            print(f"   {data.get('emotion', 'N/A')}")
            
            if 'response_time' in data:
                print(f"\n⚡ Response Time: {data['response_time']:.2f}s")
            
            # Test if audio file is accessible
            audio_url = data.get('audio_url')
            if audio_url:
                print(f"\n🎵 Testing audio file access...")
                try:
                    audio_response = requests.head(audio_url, timeout=5)
                    if audio_response.status_code == 200:
                        print("   ✅ Audio file is accessible!")
                        print(f"   💡 You can play it at: {audio_url}")
                    else:
                        print(f"   ⚠️  Audio file returned status {audio_response.status_code}")
                except Exception as e:
                    print(f"   ⚠️  Could not verify audio: {e}")
            
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (backend might be slow)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("🎤 HoloMentor Voice Pipeline Test")
    print("=" * 60)
    print()
    
    # Test 1: Backend health
    if not test_backend_health():
        print("\n" + "=" * 60)
        print("\n❌ Backend is not running!")
        print("\n📋 To start the backend:")
        print("   1. cd backend")
        print("   2. pip install -r requirements.txt")
        print("   3. python app.py")
        print("\n   Make sure you have:")
        print("   - Created .env file in project root with API keys")
        print("   - Installed all dependencies")
        print("=" * 60)
        return
    
    print("\n" + "=" * 60)
    
    # Test 2: Ask endpoint
    if test_ask_endpoint():
        print("\n" + "=" * 60)
        print("\n✅ Voice Pipeline Test Complete!")
        print("\n🎯 Next Steps:")
        print("   1. Test mobile app: cd mobile && npm start")
        print("   2. Or test audio playback in browser")
        print("   3. Check backend logs for any issues")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("\n❌ Voice pipeline test failed!")
        print("\n🔧 Troubleshooting:")
        print("   - Check backend logs for errors")
        print("   - Verify API keys in .env file")
        print("   - Ensure Groq and ElevenLabs are working")
        print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)

