# Coaching Center Recommendations Feature

## Overview

The coaching center recommendations feature uses Google Places API to suggest nearby coaching centers, classes, and training facilities based on user interests and location.

## How It Works

1. **Interest Detection**: The system extracts user interests from:
   - User profile (`learning_goals` and `preferences.interests`)
   - Recent conversations (using AI to analyze topics)

2. **Location-Based Search**: Uses Google Places API to find nearby facilities matching the detected interests

3. **Personalized Recommendations**: Returns top-rated coaching centers sorted by rating

## Setup

### 1. Get Google Places API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - **Places API** (New)
   - **Geocoding API**
4. Create credentials (API Key)
5. Add the API key to your `.env` file:
   ```
   GOOGLE_PLACES_API_KEY=your-api-key-here
   ```

### 2. Update User Profile with Location

Users need to set their location in their profile. Location can be provided in two formats:

**Option 1: City/State/Country (Recommended)**
```json
{
  "location": {
    "city": "San Francisco",
    "state": "CA",
    "country": "USA"
  }
}
```

**Option 2: Coordinates**
```json
{
  "location": {
    "lat": 37.7749,
    "lng": -122.4194
  }
}
```

### 3. Set User Interests

Interests can be set in two ways:

**Via Learning Goals:**
```json
{
  "learning_goals": ["karate", "swimming", "music"]
}
```

**Via Preferences:**
```json
{
  "preferences": {
    "interests": ["karate", "swimming"]
  }
}
```

**Automatic Detection:**
Interests are also automatically detected from conversation topics using AI.

## API Usage

### Get Coaching Center Recommendations

**Endpoint:** `GET /api/recommendations/coaching-centers`

**Headers:**
- `X-User-ID`: User identifier (required)

**Query Parameters:**
- `radius`: Search radius in meters (default: 10000 = 10km)

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/recommendations/coaching-centers?radius=5000" \
  -H "X-User-ID: user123"
```

**Example Response:**
```json
{
  "success": true,
  "user_id": "user123",
  "detected_interests": ["karate", "swimming"],
  "location": {
    "city": "San Francisco",
    "state": "CA"
  },
  "recommendations": [
    {
      "name": "Karate Dojo",
      "address": "123 Main St, San Francisco, CA 94102",
      "phone": "+1-555-123-4567",
      "website": "https://example.com",
      "rating": 4.8,
      "total_ratings": 150,
      "matched_interest": "karate",
      "coordinates": {
        "lat": 37.7749,
        "lng": -122.4194
      }
    }
  ],
  "total_found": 5
}
```

### Update User Profile with Location

**Endpoint:** `PUT /api/user/profile`

**Headers:**
- `X-User-ID`: User identifier

**Request Body:**
```json
{
  "name": "John Doe",
  "age": 15,
  "learning_goals": ["karate", "swimming"],
  "location": {
    "city": "San Francisco",
    "state": "CA",
    "country": "USA"
  }
}
```

## Supported Interest Categories

The system supports the following interest categories (automatically mapped to relevant search queries):

- **Karate** / **Martial Arts** / **Taekwondo** / **Judo** → Martial arts schools
- **Swimming** → Swimming pools and aquatic centers
- **Dance** → Dance schools
- **Music** → Music schools
- **Yoga** → Yoga studios
- **Art** → Art galleries and studios
- **Sports** (Basketball, Tennis, Soccer, Football) → Sports facilities
- **Cooking** → Culinary schools
- **Gym** → Fitness centers

## Mobile App Integration

### JavaScript Example

```javascript
// Get recommendations
async function getCoachingRecommendations(userId, radius = 10000) {
  const response = await fetch(
    `${API_BASE_URL}/recommendations/coaching-centers?radius=${radius}`,
    {
      headers: {
        'X-User-ID': userId
      }
    }
  );
  
  const data = await response.json();
  return data.recommendations;
}

// Update user location
async function updateUserLocation(userId, location) {
  const response = await fetch(`${API_BASE_URL}/user/profile`, {
    method: 'PUT',
    headers: {
      'X-User-ID': userId,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      location: location
    })
  });
  
  return await response.json();
}
```

## Error Handling

The API returns appropriate error responses:

- **400 Bad Request**: Missing user ID or location
- **404 Not Found**: User not found
- **503 Service Unavailable**: Google Places API not configured

## Cost Considerations

Google Places API offers:
- **$200 free credit per month** (equivalent to ~40,000 text search requests)
- Pay-as-you-go pricing after free tier

For most use cases, the free tier should be sufficient.

## Troubleshooting

### "Location not set" Error
- Ensure user profile includes a `location` field
- Location can be city/state/country or lat/lng coordinates

### "No interests detected" Response
- Update user profile with `learning_goals` or `preferences.interests`
- Have conversations about interests (e.g., "I want to learn karate")

### "Places service not configured" Error
- Check that `GOOGLE_PLACES_API_KEY` is set in `.env`
- Verify the API key is valid
- Ensure Places API and Geocoding API are enabled in Google Cloud Console

## Future Enhancements

Potential improvements:
- Filter by price range
- Filter by rating threshold
- Include distance calculation
- Show opening hours
- Add user reviews
- Support for more activity types
- Caching of results

