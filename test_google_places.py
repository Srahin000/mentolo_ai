#!/usr/bin/env python3
"""
Test Google Places API Service
Tests location-based coaching center recommendations
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:3001')

def print_header(text):
    print(f"\n{'='*70}")
    print(f"{text:^70}")
    print(f"{'='*70}\n")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def test_health():
    """Check if server is running and Places service is available"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            places_available = data.get('services', {}).get('places', False)
            if places_available:
                print_success("Server is running and Google Places service is available")
                return True
            else:
                print_error("Google Places service not configured")
                print_info("Add GOOGLE_PLACES_API_KEY to your .env file")
                return False
        return False
    except Exception as e:
        print_error(f"Cannot connect to server: {e}")
        return False

def test_places_endpoint():
    """Test the /api/recommendations/coaching-centers endpoint"""
    print_header("Testing Coaching Centers Recommendation Endpoint")
    
    # The endpoint expects a user_id and uses their profile location
    # For testing, we'll need to either:
    # 1. Set up a user profile with location, OR
    # 2. Test the PlacesService directly
    
    test_user_id = "test_user_places"
    
    print_info("Testing endpoint: GET /api/recommendations/coaching-centers")
    print_info("This endpoint requires:")
    print("  1. User profile with location set")
    print("  2. User interests (from profile or conversations)")
    
    try:
        # First, try to get recommendations for a test user
        response = requests.get(
            f"{BASE_URL}/api/recommendations/coaching-centers",
            headers={"X-User-ID": test_user_id},
            params={"radius": 10000},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get('recommendations', [])
            
            print_success(f"Found {len(recommendations)} recommendations")
            
            if recommendations:
                print(f"\n   Top Results:")
                for j, place in enumerate(recommendations[:3], 1):
                    print(f"   {j}. {place.get('name', 'N/A')}")
                    print(f"      Interest: {place.get('matched_interest', 'N/A')}")
                    print(f"      Address: {place.get('address', place.get('vicinity', 'N/A'))}")
                    if place.get('rating'):
                        print(f"      Rating: {place.get('rating')}/5.0 ({place.get('total_ratings', 0)} reviews)")
                    print()
            else:
                print_info("No recommendations found")
                print_info("This might mean:")
                print("  - User profile doesn't have location set")
                print("  - No interests detected for the user")
        elif response.status_code == 400:
            error_data = response.json()
            print_error(f"Bad request: {error_data.get('error', 'Unknown error')}")
            print_info(f"Message: {error_data.get('message', '')}")
        elif response.status_code == 503:
            error_data = response.json()
            print_error(f"Service unavailable: {error_data.get('error', 'Unknown error')}")
            print_info("Google Places API key might not be configured")
        else:
            print_error(f"Unexpected status: {response.status_code}")
            print_error(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print_error(f"Error testing endpoint: {e}")
    
    # Also test direct PlacesService functionality
    print("\n" + "-"*70)
    print("Testing Direct PlacesService (bypassing user profile requirement)")
    
    try:
        # Test with direct location and interest
        test_location = {"city": "New York", "state": "NY", "country": "USA"}
        test_interest = "karate"
        
        print(f"\n📍 Testing: {test_interest} in {test_location}")
        
        # We'll test this via the direct service test below
        print_info("See 'Direct Service Test' section below for detailed testing")
        
    except Exception as e:
        print_error(f"Error: {e}")

def test_direct_service():
    """Test the PlacesService directly (if running locally)"""
    print_header("Testing PlacesService Directly")
    
    try:
        from backend.services.places_service import PlacesService
        
        places_service = PlacesService()
        
        if not places_service.is_available():
            print_error("Google Places API key not configured")
            print_info("Set GOOGLE_PLACES_API_KEY in your .env file")
            return False
        
        print_success("PlacesService initialized")
        
        # Test geocoding
        print("\n📍 Testing Geocoding:")
        location = places_service._geocode_location({
            "city": "San Francisco",
            "state": "CA",
            "country": "USA"
        })
        
        if location:
            print_success(f"Geocoded location: {location}")
        else:
            print_error("Geocoding failed")
        
        # Test place search
        print("\n🔍 Testing Place Search:")
        places = places_service.search_nearby_places(
            query="karate dojo",
            location={"city": "San Francisco", "state": "CA"},
            radius=5000,
            max_results=3
        )
        
        if places:
            print_success(f"Found {len(places)} places")
            for place in places[:2]:
                print(f"   • {place.get('name')} - {place.get('vicinity', 'N/A')}")
        else:
            print_info("No places found (this might be normal if API key has restrictions)")
        
        # Test category search
        print("\n🏷️  Testing Category Search:")
        category_places = places_service.search_by_category(
            category="swimming",
            location={"city": "New York", "state": "NY"},
            radius=5000
        )
        
        if category_places:
            print_success(f"Found {len(category_places)} places for 'swimming'")
        else:
            print_info("No places found for this category")
        
        return True
        
    except ImportError:
        print_info("Cannot import PlacesService directly (running from wrong directory)")
        return False
    except Exception as e:
        print_error(f"Error testing service directly: {e}")
        return False

def main():
    print_header("🧪 Google Places API Test")
    
    # Check API key
    api_key = os.getenv('GOOGLE_PLACES_API_KEY')
    if not api_key or api_key == 'your-google-places-api-key-here':
        print_error("GOOGLE_PLACES_API_KEY not set in .env file")
        print_info("Get your API key from: https://console.cloud.google.com/apis/credentials")
        print_info("Enable 'Places API' and 'Geocoding API' in Google Cloud Console")
        return
    
    # Test 1: Health check
    if not test_health():
        print_error("Server or Places service not available")
        print_info("Make sure:")
        print("   1. Server is running: cd backend && python app.py")
        print("   2. GOOGLE_PLACES_API_KEY is set in .env")
        return
    
    # Test 2: API endpoint
    test_places_endpoint()
    
    # Test 3: Direct service (optional)
    print("\n" + "="*70)
    test_direct_service()
    
    print_header("📊 Test Complete")
    print_success("Google Places API testing finished!")
    print_info("Check the results above to verify the service is working correctly")

if __name__ == "__main__":
    main()

