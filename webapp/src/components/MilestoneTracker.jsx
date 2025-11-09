import React from 'react';
import { CheckCircle2, Clock, AlertCircle } from 'lucide-react';

export default function MilestoneTracker({ milestoneProgress = {} }) {
  const milestones = [
    {
      category: 'Language & Communication',
      items: [
        { name: 'Uses 4-5 word sentences', status: 'mastered' },
        { name: 'Tells stories with details', status: 'mastered' },
        { name: 'Asks "why" questions', status: 'emerging' },
        { name: 'Speaks clearly to strangers', status: 'on_track' },
      ],
    },
    {
      category: 'Cognitive & Learning',
      items: [
        { name: 'Counts to 10', status: 'mastered' },
        { name: 'Understands time concepts', status: 'emerging' },
        { name: 'Sorts by color/size', status: 'mastered' },
        { name: 'Solves simple puzzles', status: 'on_track' },
      ],
    },
  ];

  // Use provided milestone progress if available
  const progressData = milestoneProgress.on_track || milestoneProgress.emerging || milestoneProgress.ahead
    ? milestoneProgress
    : null;

  const getStatusIcon = (status) => {
    switch (status) {
      case 'mastered':
      case 'ahead':
        return <CheckCircle2 className="status-icon mastered" />;
      case 'emerging':
        return <Clock className="status-icon emerging" />;
      case 'on_track':
        return <CheckCircle2 className="status-icon on-track" />;
      default:
        return <AlertCircle className="status-icon watching" />;
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'mastered':
      case 'ahead':
        return 'Mastered';
      case 'emerging':
        return 'Emerging';
      case 'on_track':
        return 'On Track';
      default:
        return 'Keep Watching';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'mastered':
      case 'ahead':
        return '#50C878';
      case 'emerging':
        return '#FFB347';
      case 'on_track':
        return '#4A90E2';
      default:
        return '#FF8C69';
    }
  };

  return (
    <div className="milestone-tracker">
      <h3 className="section-title">Developmental Milestones Tracker</h3>
      {milestones.map((category, catIndex) => (
        <div key={catIndex} className="milestone-category">
          <h4 className="category-title">{category.category}</h4>
          <div className="milestone-items">
            {category.items.map((item, itemIndex) => (
              <div key={itemIndex} className="milestone-item">
                <div className="milestone-header">
                  <div className="milestone-status">
                    {getStatusIcon(item.status)}
                    <span
                      className="status-badge"
                      style={{ color: getStatusColor(item.status) }}
                    >
                      {getStatusLabel(item.status)}
                    </span>
                  </div>
                </div>
                <span className="milestone-name">{item.name}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

