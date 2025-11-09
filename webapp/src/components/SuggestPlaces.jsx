/**
 * Suggest Places Component
 * Simple card that expands to show place recommendations
 */

import React, { useState } from 'react';
import { MapPin, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';
import PlacesRecommendations from './PlacesRecommendations';
import './SuggestPlaces.css';

export default function SuggestPlaces({ childId, childName = 'Your child' }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className={`suggest-places ${isExpanded ? 'expanded' : ''}`}>
      <div 
        className="suggest-places-header"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="suggest-places-title">
          <MapPin size={24} />
          <div>
            <h3>Suggest places to go with {childName}</h3>
            <p className="suggest-places-subtitle">Find activities and learning centers nearby</p>
          </div>
        </div>
        {isExpanded ? <ChevronUp size={24} /> : <ChevronDown size={24} />}
      </div>
      
      {isExpanded && (
        <div className="suggest-places-content">
          <PlacesRecommendations childId={childId} childName={childName} />
        </div>
      )}
    </div>
  );
}

