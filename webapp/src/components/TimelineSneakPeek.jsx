/**
 * Timeline Sneak Peek Component
 * Simple bar showing growth trend
 */

import React from 'react';
import { TrendingUp, Calendar } from 'lucide-react';
import './TimelineSneakPeek.css';

export default function TimelineSneakPeek({ sessions = [], childName = 'Your child' }) {
  // Calculate streak (consecutive weeks with sessions)
  const weeksWithSessions = new Set();
  sessions.forEach(session => {
    if (session.timestamp) {
      const date = new Date(session.timestamp);
      const week = `${date.getFullYear()}-W${getWeekNumber(date)}`;
      weeksWithSessions.add(week);
    }
  });

  const streak = weeksWithSessions.size;
  const message = streak >= 3 
    ? `Steady growth for ${streak} weeks in a row!`
    : streak >= 1
    ? `Building momentum with ${streak} week${streak > 1 ? 's' : ''} of progress!`
    : 'Getting started!';

  return (
    <div className="timeline-sneak-peek">
      <div className="timeline-header">
        <Calendar size={18} />
        <h3>Timeline</h3>
      </div>
      
      <div className="timeline-content">
        <div className="timeline-message">
          <TrendingUp size={16} />
          <span>{message}</span>
        </div>
        
        {/* Simple progress bar representing weeks */}
        <div className="timeline-bars">
          {Array.from({ length: Math.min(streak, 8) }).map((_, i) => (
            <div 
              key={i} 
              className="timeline-bar"
              style={{ 
                height: `${60 + (i * 5)}%`,
                animationDelay: `${i * 0.1}s`
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

// Helper function to get week number
function getWeekNumber(date) {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  const dayNum = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
}

