import React from 'react';
import { Brain, Heart, Users, Lightbulb, MessageSquare, Activity } from 'lucide-react';

const developmentAreas = [
  { id: 'language', label: 'Language', icon: MessageSquare, color: '#3B82F6' },
  { id: 'cognitive', label: 'Cognitive', icon: Brain, color: '#8B5CF6' },
  { id: 'emotional', label: 'Emotional', icon: Heart, color: '#EC4899' },
  { id: 'social', label: 'Social', icon: Users, color: '#10B981' },
  { id: 'creativity', label: 'Creativity', icon: Lightbulb, color: '#F59E0B' },
  { id: 'physical', label: 'Physical', icon: Activity, color: '#EF4444' },
];

export default function DevelopmentSnapshotGrid({ snapshot = {} }) {
  const getLevelColor = (level) => {
    if (!level) return '#ccc';
    const levelLower = level.toLowerCase();
    if (levelLower.includes('strong') || levelLower.includes('ahead')) return '#50C878';
    if (levelLower.includes('growing') || levelLower.includes('emerging')) return '#FFB347';
    if (levelLower.includes('developing')) return '#FF8C69';
    return '#ccc';
  };

  const getLevelIcon = (level) => {
    if (!level) return null;
    const levelLower = level.toLowerCase();
    if (levelLower.includes('strong') || levelLower.includes('ahead')) return '✓';
    if (levelLower.includes('growing') || levelLower.includes('emerging')) return '→';
    if (levelLower.includes('developing')) return '○';
    return null;
  };

  return (
    <div className="development-grid">
      <h3 className="section-title">Development Snapshot</h3>
      <div className="grid-container">
        {developmentAreas.map((area) => {
          const areaData = snapshot[area.id] || {};
          const Icon = area.icon;
          const score = areaData.score || 0;
          const level = areaData.level || 'Not assessed';

          return (
            <div key={area.id} className="dev-card">
              <div className="dev-card-header">
                <Icon className="dev-icon" style={{ color: area.color }} />
                <h4>{area.label}</h4>
              </div>
              <div className="dev-score">
                <span className="score-number">{score}</span>
                <span className="score-label">/100</span>
              </div>
              <div className="dev-level">
                {getLevelIcon(level) && <span className="level-indicator">{getLevelIcon(level)}</span>}
                <span className="level-text">{level}</span>
              </div>
              <div className="dev-progress-bar">
                <div
                  className="dev-progress-fill"
                  style={{
                    width: `${score}%`,
                    backgroundColor: getLevelColor(level),
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

