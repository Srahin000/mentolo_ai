"""
Google Places API Service - Location-based Coaching Center Recommendations
"""

import os
import logging
import requests
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PlacesService:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        self.base_url = 'https://maps.googleapis.com/maps/api/place'
        
        if self.api_key:
            logger.info("Google Places service initialized")
        else:
            logger.warning("Google Places API key not found")
    
    def is_available(self):
        """Check if Places service is available"""
        return self.api_key is not None
    
    def search_nearby_places(self, query: str, location: Dict, radius: int = 5000, 
                            max_results: int = 10) -> List[Dict]:
        """
        Search for places near a location
        
        Args:
            query: Search query (e.g., "karate dojo", "martial arts school")
            location: Dict with 'lat' and 'lng' or 'city' and 'state'
            radius: Search radius in meters (default: 5000 = 5km)
            max_results: Maximum number of results to return
        
        Returns:
            List of place dictionaries with details
        """
        if not self.api_key:
            raise Exception("Google Places API key not configured")
        
        try:
            # Convert city/state to coordinates if needed
            if 'lat' not in location or 'lng' not in location:
                location = self._geocode_location(location)
                if not location:
                    return []
            
            # Use Text Search API (better for specific queries)
            url = f"{self.base_url}/textsearch/json"
            params = {
                'query': query,
                'location': f"{location['lat']},{location['lng']}",
                'radius': radius,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') != 'OK':
                logger.error(f"Places API error: {data.get('status')}")
                return []
            
            places = []
            for result in data.get('results', [])[:max_results]:
                place_details = self._format_place_result(result)
                
                # Get detailed information
                details = self.get_place_details(place_details['place_id'])
                if details:
                    place_details.update(details)
                
                places.append(place_details)
            
            logger.info(f"Found {len(places)} places for query: {query}")
            return places
            
        except Exception as e:
            logger.error(f"Error searching places: {e}")
            return []
    
    def search_by_category(self, category: str, location: Dict, radius: int = 5000) -> List[Dict]:
        """
        Search for places by category using category mapping
        
        Args:
            category: Interest category (e.g., "karate", "swimming", "dance")
            location: Location dict
            radius: Search radius in meters
        """
        # Map interests to Google Places types/categories
        category_mapping = {
            'karate': 'martial_arts_school',
            'martial_arts': 'martial_arts_school',
            'taekwondo': 'martial_arts_school',
            'judo': 'martial_arts_school',
            'swimming': 'swimming_pool',
            'dance': 'dance_school',
            'music': 'music_school',
            'yoga': 'yoga_studio',
            'gym': 'gym',
            'basketball': 'basketball_court',
            'tennis': 'tennis_court',
            'soccer': 'soccer_field',
            'football': 'stadium',
            'cooking': 'restaurant',  # Fallback
            'art': 'art_gallery',
        }
        
        # Get the query string
        place_type = category_mapping.get(category.lower(), category)
        location_str = location.get('city', '')
        if location.get('state'):
            location_str += f", {location.get('state')}"
        if location.get('country'):
            location_str += f", {location.get('country')}"
        
        query = f"{category} classes {location_str}".strip()
        
        return self.search_nearby_places(query, location, radius)
    
    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information about a place"""
        if not self.api_key:
            return None
        
        try:
            url = f"{self.base_url}/details/json"
            params = {
                'place_id': place_id,
                'fields': 'name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,opening_hours,photos,geometry',
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'OK' and 'result' in data:
                result = data['result']
                return {
                    'address': result.get('formatted_address'),
                    'phone': result.get('formatted_phone_number'),
                    'website': result.get('website'),
                    'rating': result.get('rating'),
                    'total_ratings': result.get('user_ratings_total'),
                    'opening_hours': result.get('opening_hours', {}).get('weekday_text', []),
                    'coordinates': {
                        'lat': result.get('geometry', {}).get('location', {}).get('lat'),
                        'lng': result.get('geometry', {}).get('location', {}).get('lng')
                    }
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting place details: {e}")
            return None
    
    def _geocode_location(self, location: Dict) -> Optional[Dict]:
        """Convert city/state to coordinates"""
        if not self.api_key:
            return None
        
        try:
            city = location.get('city', '')
            state = location.get('state', '')
            country = location.get('country', '')
            
            query = f"{city}, {state}, {country}".strip(', ')
            
            url = f"https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': query,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'OK' and data.get('results'):
                location_data = data['results'][0]['geometry']['location']
                return {
                    'lat': location_data['lat'],
                    'lng': location_data['lng']
                }
            return None
            
        except Exception as e:
            logger.error(f"Error geocoding location: {e}")
            return None
    
    def _format_place_result(self, result: Dict) -> Dict:
        """Format a place result from API"""
        return {
            'place_id': result.get('place_id'),
            'name': result.get('name'),
            'rating': result.get('rating'),
            'total_ratings': result.get('user_ratings_total', 0),
            'vicinity': result.get('formatted_address') or result.get('vicinity'),
            'types': result.get('types', [])
        }

