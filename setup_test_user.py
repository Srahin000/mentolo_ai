#!/usr/bin/env python3
"""
Setup test user profile with location and interests for Google Places testing
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:3001')
TEST_USER_ID = "test_user_places"

def setup_test_user():
    """Create a test user profile with location and interests"""
    
    print("🔧 Setting up test user profile...")
    
    # User profile data
    profile_data = {
        "name": "Test User",
        "age": 8,
        "location": {
            "city": "New York",
            "state": "NY",
            "country": "USA"
        },
        "learning_goals": ["karate", "swimming", "dance"],
        "preferences": {
            "interests": ["martial arts", "sports", "dance"],
            "activity_types": ["physical", "competitive"]
        }
    }
    
    try:
        # Create/update user profile
        response = requests.put(
            f"{BASE_URL}/api/user/profile",
            headers={"X-User-ID": TEST_USER_ID},
            json=profile_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ User profile created/updated successfully")
            print(f"   User ID: {TEST_USER_ID}")
            print(f"   Location: {profile_data['location']}")
            print(f"   Interests: {profile_data['learning_goals']}")
            return True
        else:
            print(f"❌ Failed to create profile: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up user: {e}")
        return False

def verify_user_profile():
    """Verify the user profile was created"""
    print("\n🔍 Verifying user profile...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/user/profile",
            headers={"X-User-ID": TEST_USER_ID},
            timeout=10
        )
        
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ Profile verified")
            print(f"   Name: {profile.get('name', 'N/A')}")
            print(f"   Location: {profile.get('location', 'N/A')}")
            print(f"   Learning Goals: {profile.get('learning_goals', [])}")
            return True
        else:
            print(f"❌ Profile not found: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying profile: {e}")
        return False

def test_coaching_centers():
    """Test the coaching centers endpoint with the test user"""
    print("\n📍 Testing Coaching Centers Endpoint...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/recommendations/coaching-centers",
            headers={"X-User-ID": TEST_USER_ID},
            params={"radius": 10000},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get('recommendations', [])
            interests = data.get('detected_interests', [])
            
            print(f"✅ Successfully retrieved recommendations!")
            print(f"\n📊 Summary:")
            print(f"   Detected Interests: {interests}")
            print(f"   Total Recommendations: {len(recommendations)}")
            print(f"   Location: {data.get('location', 'N/A')}")
            
            if recommendations:
                print(f"\n🏆 Top Recommendations:")
                for i, place in enumerate(recommendations[:5], 1):
                    print(f"\n   {i}. {place.get('name', 'N/A')}")
                    print(f"      Interest: {place.get('matched_interest', 'N/A')}")
                    print(f"      Address: {place.get('address', place.get('vicinity', 'N/A'))}")
                    if place.get('rating'):
                        print(f"      ⭐ Rating: {place.get('rating')}/5.0 ({place.get('total_ratings', 0)} reviews)")
                    if place.get('phone'):
                        print(f"      📞 Phone: {place.get('phone')}")
                    if place.get('website'):
                        print(f"      🌐 Website: {place.get('website')}")
            else:
                print("\n⚠️  No recommendations found")
                print("   This might mean:")
                print("   - No places found in the specified radius")
                print("   - API key restrictions")
                print("   - Location not geocoded correctly")
            
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return False

def main():
    print("="*70)
    print("🧪 Setting Up Test User for Google Places API")
    print("="*70)
    
    # Step 1: Setup user profile
    if not setup_test_user():
        print("\n❌ Failed to setup user profile")
        return
    
    # Step 2: Verify profile
    if not verify_user_profile():
        print("\n⚠️  Profile verification failed, but continuing...")
    
    # Step 3: Test coaching centers endpoint
    print("\n" + "="*70)
    test_coaching_centers()
    
    print("\n" + "="*70)
    print("✅ Setup and testing complete!")
    print(f"   Test User ID: {TEST_USER_ID}")
    print("   You can now use this user ID to test the endpoint")

if __name__ == "__main__":
    main()

