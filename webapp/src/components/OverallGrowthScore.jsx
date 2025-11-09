/**
 * Overall Growth Score Component
 * Single friendly number (0-100) with trend indicator
 */

import React from 'react';
import { TrendingUp, TrendingDown, Minus, Smile } from 'lucide-react';
import './OverallGrowthScore.css';

export default function OverallGrowthScore({ score = 0, trend = 0, sessions = [] }) {
  // Calculate average score from sessions if not provided
  if (score === 0 && sessions.length > 0) {
    const scores = sessions
      .filter(s => s.language_score || s.cognitive_score || s.emotional_score)
      .map(s => {
        const lang = s.language_score || 0;
        const cog = s.cognitive_score || 0;
        const emo = s.emotional_score || 0;
        const soc = s.social_score || 0;
        const cre = s.creativity_score || 0;
        return (lang + cog + emo + soc + cre) / 5;
      });
    
    if (scores.length > 0) {
      score = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
    }
  }

  // Determine status and color
  let status, statusColor, statusIcon, statusMessage;
  if (score >= 80) {
    status = 'thriving';
    statusColor = '#10B981'; // green
    statusIcon = <Smile size={24} />;
    statusMessage = 'Growing beautifully!';
  } else if (score >= 60) {
    status = 'growing';
    statusColor = '#F59E0B'; // yellow
    statusIcon = <Smile size={24} />;
    statusMessage = 'Doing fine, a few areas to help with.';
  } else {
    status = 'exploring';
    statusColor = '#3B82F6'; // blue
    statusIcon = <Smile size={24} />;
    statusMessage = 'Exploring and learning!';
  }

  // Trend indicator
  let trendIcon, trendText, trendColor;
  if (trend > 0) {
    trendIcon = <TrendingUp size={16} />;
    trendText = `+${Math.round(trend)} this month`;
    trendColor = '#10B981';
  } else if (trend < 0) {
    trendIcon = <TrendingDown size={16} />;
    trendText = `${Math.round(trend)} this month`;
    trendColor = '#EF4444';
  } else {
    trendIcon = <Minus size={16} />;
    trendText = 'Steady this month';
    trendColor = '#6B7280';
  }

  return (
    <div className="overall-growth-score" style={{ '--status-color': statusColor }}>
      <div className="growth-score-header">
        <h2>Overall Growth Score</h2>
        <div className="status-indicator" style={{ color: statusColor }}>
          {statusIcon}
        </div>
      </div>
      
      <div className="growth-score-main">
        <div className="score-number" style={{ color: statusColor }}>
          {Math.round(score)}
        </div>
        <div className="score-label">/100</div>
      </div>
      
      <div className="growth-status-message" style={{ color: statusColor }}>
        {statusMessage}
      </div>
      
      <div className="growth-trend" style={{ color: trendColor }}>
        {trendIcon}
        <span>{trendText}</span>
      </div>
      
      {/* Simple progress bar */}
      <div className="growth-progress-bar">
        <div 
          className="growth-progress-fill" 
          style={{ 
            width: `${score}%`,
            backgroundColor: statusColor
          }}
        />
      </div>
    </div>
  );
}

