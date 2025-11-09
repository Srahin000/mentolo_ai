import React from 'react';
import { Trophy, Star, Award } from 'lucide-react';

export default function StrengthSpotlight({ strengths = [], childName = 'Your child' }) {
  if (!strengths || strengths.length === 0) {
    return (
      <div className="strength-spotlight">
        <h3 className="section-title">
          <Trophy className="icon" />
          {childName}'s Superpowers
        </h3>
        <p className="empty-state">No strengths identified yet. Keep having conversations!</p>
      </div>
    );
  }

  return (
    <div className="strength-spotlight">
      <h3 className="section-title">
        <Trophy className="icon" />
        {childName}'s Superpowers
      </h3>
      <div className="strengths-grid">
        {strengths.map((strength, index) => (
          <div key={index} className="strength-card">
            <div className="strength-badge">
              {index === 0 && <Trophy className="badge-icon" />}
              {index === 1 && <Star className="badge-icon" />}
              {index === 2 && <Award className="badge-icon" />}
              {index > 2 && <Star className="badge-icon" />}
            </div>
            <h4 className="strength-title">{strength.title || strength.name}</h4>
            <p className="strength-evidence">{strength.evidence || strength.description}</p>
            {strength.why_matters && (
              <p className="strength-impact">
                <strong>Why it matters:</strong> {strength.why_matters}
              </p>
            )}
            <button className="btn-share-achievement">Share Achievement</button>
          </div>
        ))}
      </div>
    </div>
  );
}

