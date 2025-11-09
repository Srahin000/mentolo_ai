/**
 * Area to Nurture Component
 * Shows one growth area with simple, actionable guidance
 */

import React from 'react';
import { Heart, ArrowRight } from 'lucide-react';
import './AreaToNurture.css';

export default function AreaToNurture({ growthArea, childName = 'Your child' }) {
  if (!growthArea) {
    return null;
  }

  // Extract growth area info
  const area = growthArea.area || growthArea.title || 'Growth Opportunity';
  const nextStep = growthArea.next_step || growthArea.recommendation || `Try activities together to support ${area.toLowerCase()}`;

  return (
    <div className="area-to-nurture">
      <div className="nurture-header">
        <div className="nurture-icon">
          <Heart size={24} />
        </div>
        <h3>Area to Nurture</h3>
      </div>
      
      <div className="nurture-content">
        <div className="nurture-title">
          <span>{area}</span>
        </div>
        <p className="nurture-guidance">
          {nextStep}
        </p>
      </div>
    </div>
  );
}

