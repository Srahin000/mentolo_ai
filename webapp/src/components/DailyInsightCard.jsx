import React from 'react';
import { Sparkles, Share2 } from 'lucide-react';

export default function DailyInsightCard({ insight, childName = 'Your child' }) {
  if (!insight) {
    return (
      <div className="daily-insight-card">
        <div className="insight-header">
          <Sparkles className="icon" />
          <h2>TODAY'S INSIGHT</h2>
        </div>
        <p className="insight-placeholder">No insights available yet. Start a conversation to see insights!</p>
      </div>
    );
  }

  return (
    <div className="daily-insight-card">
      <div className="insight-header">
        <Sparkles className="icon" />
        <h2>TODAY'S INSIGHT</h2>
        <button className="share-button" aria-label="Share insight">
          <Share2 size={18} />
        </button>
      </div>
      <div className="insight-content">
        <p className="insight-text">{insight}</p>
      </div>
      <div className="insight-actions">
        <button className="btn-secondary">View Details</button>
        <button className="btn-secondary">Share with Partner</button>
      </div>
    </div>
  );
}

