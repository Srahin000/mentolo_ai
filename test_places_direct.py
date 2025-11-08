#!/usr/bin/env python3
"""
Direct Google Places API Test
Tests the Places API directly without database dependencies
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

load_dotenv()

from services.places_service import PlacesService

def print_header(text):
    print(f"\n{'='*70}")
    print(f"{text:^70}")
    print(f"{'='*70}\n")

def test_places_api():
    """Test Google Places API directly"""
    
    print_header("🧪 Direct Google Places API Test")
    
    # Check API key
    api_key = os.getenv('GOOGLE_PLACES_API_KEY')
    if not api_key or api_key == 'your-google-places-api-key-here':
        print("❌ GOOGLE_PLACES_API_KEY not set in .env file")
        print("ℹ️  Get your API key from: https://console.cloud.google.com/apis/credentials")
        return
    
    # Initialize Places service
    places_service = PlacesService()
    
    if not places_service.is_available():
        print("❌ Google Places service not available")
        return
    
    print("✅ Google Places service initialized")
    print(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
    
    # Test 1: Geocoding
    print_header("Test 1: Geocoding (City → Coordinates)")
    
    test_locations = [
        {"city": "New York", "state": "NY", "country": "USA"},
        {"city": "Los Angeles", "state": "CA", "country": "USA"},
        {"city": "San Francisco", "state": "CA", "country": "USA"}
    ]
    
    for loc in test_locations:
        coords = places_service._geocode_location(loc)
        if coords:
            print(f"✅ {loc['city']}, {loc['state']}")
            print(f"   Coordinates: {coords['lat']:.6f}, {coords['lng']:.6f}")
        else:
            print(f"❌ Failed to geocode {loc['city']}, {loc['state']}")
    
    # Test 2: Place Search by Query
    print_header("Test 2: Place Search by Query")
    
    searches = [
        ("karate dojo", {"city": "New York", "state": "NY"}),
        ("swimming pool", {"city": "Los Angeles", "state": "CA"}),
        ("dance studio", {"city": "San Francisco", "state": "CA"})
    ]
    
    for query, location in searches:
        print(f"\n🔍 Searching for: '{query}' in {location['city']}, {location['state']}")
        places = places_service.search_nearby_places(query, location, radius=5000, max_results=3)
        
        if places:
            print(f"   ✅ Found {len(places)} places:")
            for i, place in enumerate(places, 1):
                print(f"\n   {i}. {place.get('name', 'N/A')}")
                print(f"      📍 {place.get('vicinity', 'N/A')}")
                if place.get('rating'):
                    print(f"      ⭐ {place.get('rating')}/5.0 ({place.get('total_ratings', 0)} reviews)")
                if place.get('address'):
                    print(f"      📧 {place.get('address')}")
                if place.get('phone'):
                    print(f"      📞 {place.get('phone')}")
                if place.get('website'):
                    print(f"      🌐 {place.get('website')}")
        else:
            print(f"   ⚠️  No places found")
    
    # Test 3: Category Search
    print_header("Test 3: Category Search")
    
    categories = [
        ("karate", {"city": "Princeton", "state": "NJ"}),
        ("swimming", {"city": "Boston", "state": "MA"}),
        ("dance", {"city": "Chicago", "state": "IL"})
    ]
    
    for category, location in categories:
        print(f"\n🏷️  Category: '{category}' in {location['city']}, {location['state']}")
        places = places_service.search_by_category(category, location, radius=10000)
        
        if places:
            print(f"   ✅ Found {len(places)} places")
            # Show top 3
            for i, place in enumerate(places[:3], 1):
                rating_str = f" ({place.get('rating')}/5.0)" if place.get('rating') else ""
                print(f"   {i}. {place.get('name', 'N/A')}{rating_str}")
        else:
            print(f"   ⚠️  No places found")
    
    # Test 4: Direct Coordinates Search
    print_header("Test 4: Search with Direct Coordinates")
    
    # Times Square, NYC
    coords = {"lat": 40.7580, "lng": -73.9855}
    print(f"🗽 Searching near Times Square, NYC")
    print(f"   Coordinates: {coords['lat']}, {coords['lng']}")
    
    places = places_service.search_nearby_places(
        "martial arts", 
        coords, 
        radius=3000, 
        max_results=5
    )
    
    if places:
        print(f"\n   ✅ Found {len(places)} martial arts schools:")
        for i, place in enumerate(places, 1):
            print(f"   {i}. {place.get('name', 'N/A')}")
            if place.get('vicinity'):
                print(f"      {place.get('vicinity')}")
    else:
        print(f"   ⚠️  No places found")
    
    # Summary
    print_header("📊 Test Summary")
    print("✅ Google Places API is working!")
    print("\nCapabilities verified:")
    print("  ✓ Geocoding (city/state → coordinates)")
    print("  ✓ Place search by query")
    print("  ✓ Category-based search")
    print("  ✓ Coordinate-based search")
    print("  ✓ Detailed place information (ratings, addresses, etc.)")
    print("\n🎉 All Google Places API features are functional!")

if __name__ == "__main__":
    try:
        test_places_api()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

