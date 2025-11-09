import React, { useState, useEffect } from 'react';
import { MapPin, Star, Phone, Globe, ExternalLink, Loader2, AlertCircle } from 'lucide-react';
import { getCoachingCenters } from '../services/api';
import './PlacesRecommendations.css';

export default function PlacesRecommendations({ childId, childName = 'Your child' }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [interests, setInterests] = useState([]);
  const [location, setLocation] = useState(null);

  useEffect(() => {
    if (childId) {
      loadRecommendations();
    }
  }, [childId]);

  const loadRecommendations = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await getCoachingCenters(childId, 15000); // 15km radius
      if (data.success) {
        setRecommendations(data.recommendations || []);
        setInterests(data.detected_interests || []);
        setLocation(data.location);
      } else {
        setError(data.message || 'Failed to load recommendations');
      }
    } catch (err) {
      console.error('Error loading recommendations:', err);
      setError(err.message || 'Failed to load place recommendations');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="places-recommendations">
        <h3 className="section-title">
          <MapPin className="icon" />
          Places to Visit
        </h3>
        <div className="loading-state">
          <Loader2 className="spinner" />
          <p>Finding great places near you...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="places-recommendations">
        <h3 className="section-title">
          <MapPin className="icon" />
          Places to Visit
        </h3>
        <div className="error-state">
          <AlertCircle className="error-icon" />
          <p>{error}</p>
          {error.includes('Location not set') && (
            <p className="error-hint">Update your profile with your location to see recommendations!</p>
          )}
        </div>
      </div>
    );
  }

  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="places-recommendations">
        <h3 className="section-title">
          <MapPin className="icon" />
          Places to Visit
        </h3>
        <div className="empty-state">
          <p>No places found yet. Keep having conversations so we can learn about {childName}'s interests!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="places-recommendations">
      <h3 className="section-title">
        <MapPin className="icon" />
        Places to Visit
      </h3>

      {/* Detected Interests */}
      {interests.length > 0 && (
        <div className="interests-badge">
          <span className="badge-label">Based on interests:</span>
          <div className="interests-list">
            {interests.map((interest, index) => (
              <span key={index} className="interest-tag">{interest}</span>
            ))}
          </div>
        </div>
      )}

      {/* Location Info */}
      {location && (
        <div className="location-info">
          <MapPin size={16} />
          <span>
            {location.city && `${location.city}, `}
            {location.state && `${location.state}`}
            {location.country && `, ${location.country}`}
          </span>
        </div>
      )}

      {/* Top 5 Recommendations with Explanations */}
      <div className="places-list">
        {recommendations.map((place, index) => (
          <div key={place.place_id || index} className="place-card">
            <div className="place-number">{index + 1}</div>
            
            <div className="place-content">
              <div className="place-header">
                <h4 className="place-name">{place.name}</h4>
                {place.matched_interest && (
                  <span className="interest-match">{place.matched_interest}</span>
                )}
              </div>

              {/* Explanation - Why this place */}
              {place.explanation && (
                <div className="place-explanation">
                  <p>{place.explanation}</p>
                </div>
              )}

              {/* Rating */}
              {place.rating && (
                <div className="place-rating">
                  <Star className="star-icon" fill="currentColor" />
                  <span className="rating-value">{place.rating.toFixed(1)}</span>
                  {place.total_ratings && (
                    <span className="rating-count">({place.total_ratings} reviews)</span>
                  )}
                </div>
              )}

              {/* Address */}
              {place.address && (
                <div className="place-address">
                  <MapPin size={14} />
                  <span>{place.address}</span>
                </div>
              )}

              {/* Contact Info */}
              <div className="place-contact">
                {place.phone && (
                  <a href={`tel:${place.phone}`} className="contact-link">
                    <Phone size={14} />
                    <span>{place.phone}</span>
                  </a>
                )}
                {place.website && (
                  <a 
                    href={place.website} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="contact-link"
                  >
                    <Globe size={14} />
                    <span>Website</span>
                    <ExternalLink size={12} />
                  </a>
                )}
              </div>

              {/* Google Maps Link */}
              {place.coordinates && (
                <a
                  href={`https://www.google.com/maps/search/?api=1&query=${place.coordinates.lat},${place.coordinates.lng}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="maps-link"
                >
                  <MapPin size={14} />
                  <span>View on Google Maps</span>
                  <ExternalLink size={12} />
                </a>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Refresh Button */}
      <button onClick={loadRecommendations} className="btn-refresh-places">
        <MapPin size={16} />
        Refresh Recommendations
      </button>
    </div>
  );
}

