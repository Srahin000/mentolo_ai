/**
 * This Week's Strength Component
 * Shows one key strength with emotional, positive messaging
 */

import React from 'react';
import { Lightbulb, Sparkles } from 'lucide-react';
import './ThisWeeksStrength.css';

export default function ThisWeeksStrength({ strength, childName = 'Your child' }) {
  if (!strength) {
    return null;
  }

  // Extract strength info
  const title = strength.title || strength.area || 'Great Progress';
  const evidence = strength.evidence || strength.why_matters || 'Showing wonderful development!';

  return (
    <div className="this-weeks-strength">
      <div className="strength-header">
        <div className="strength-icon">
          <Sparkles size={24} />
        </div>
        <h3>This Week's Strength</h3>
      </div>
      
      <div className="strength-content">
        <div className="strength-title">
          <Lightbulb size={20} />
          <span>{title}</span>
        </div>
        <p className="strength-evidence">{evidence}</p>
      </div>
    </div>
  );
}

