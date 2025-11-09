/**
 * Simple Next Step Card
 * One actionable activity with "Mark as Done" button
 */

import React, { useState } from 'react';
import { CheckCircle2, Circle, Target } from 'lucide-react';
import './SimpleNextStep.css';

export default function SimpleNextStep({ activity, onComplete }) {
  const [completed, setCompleted] = useState(false);

  if (!activity) {
    return null;
  }

  const handleComplete = () => {
    setCompleted(true);
    if (onComplete) {
      onComplete(activity);
    }
  };

  const title = activity.title || 'Activity';
  const duration = activity.duration || '10 min';
  const impact = activity.impact_areas || activity.instructions || 'Supports development';

  return (
    <div className={`simple-next-step ${completed ? 'completed' : ''}`}>
      <div className="next-step-header">
        <Target size={20} />
        <h3>Suggested Activity</h3>
      </div>
      
      <div className="next-step-content">
        <div className="activity-title">{title}</div>
        <div className="activity-duration">{duration}</div>
        <div className="activity-impact">→ {impact}</div>
      </div>
      
      <button 
        className={`mark-done-btn ${completed ? 'done' : ''}`}
        onClick={handleComplete}
        disabled={completed}
      >
        {completed ? (
          <>
            <CheckCircle2 size={18} />
            <span>Done!</span>
          </>
        ) : (
          <>
            <Circle size={18} />
            <span>Mark as Done</span>
          </>
        )}
      </button>
    </div>
  );
}

