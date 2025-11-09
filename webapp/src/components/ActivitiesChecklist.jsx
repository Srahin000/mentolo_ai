import React, { useState } from 'react';
import { CheckCircle2, Circle, Target } from 'lucide-react';

export default function ActivitiesChecklist({ activities = [] }) {
  const [completedActivities, setCompletedActivities] = useState(new Set());

  const toggleActivity = (index) => {
    const newCompleted = new Set(completedActivities);
    const wasCompleted = newCompleted.has(index);
    
    if (wasCompleted) {
      newCompleted.delete(index);
    } else {
      newCompleted.add(index);
    }
    setCompletedActivities(newCompleted);
  };

  if (!activities || activities.length === 0) {
    return (
      <div className="activities-checklist">
        <h3 className="section-title">
          <Target className="icon" />
          This Week's Focus Activities
        </h3>
        <p className="empty-state">No activities suggested yet. Check back soon!</p>
      </div>
    );
  }

  return (
    <div className="activities-checklist">
      <h3 className="section-title">
        <Target className="icon" />
        This Week's Focus Activities
      </h3>
      <div className="activities-list">
        {activities.map((activity, index) => {
          const isCompleted = completedActivities.has(index);
          
          return (
            <div key={index} className={`activity-item ${isCompleted ? 'completed' : ''}`}>
              <button
                className="activity-checkbox"
                onClick={() => toggleActivity(index)}
                aria-label={`Mark ${activity.title} as ${isCompleted ? 'incomplete' : 'complete'}`}
              >
                {isCompleted ? (
                  <CheckCircle2 className="checkbox-icon checked" />
                ) : (
                  <Circle className="checkbox-icon" />
                )}
              </button>
              <div className="activity-content">
                <h4 className="activity-title">{activity.title}</h4>
                <div className="activity-meta">
                  <span className="activity-duration">{activity.duration || '10 minutes'}</span>
                  {activity.impact_areas && (
                    <span className="activity-impact">
                      Impact: {activity.impact_areas.join(', ')}
                    </span>
                  )}
                </div>
                {activity.instructions && (
                  <p className="activity-instructions">{activity.instructions}</p>
                )}
                {activity.materials && activity.materials.length > 0 && (
                  <div className="activity-materials">
                    <strong>Materials needed:</strong> {activity.materials.join(', ')}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
      <button className="btn-see-more">See More Activities</button>
    </div>
  );
}

