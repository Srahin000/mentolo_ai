/**
 * Expandable Section Component
 * Shows/hides detailed charts and metrics
 */

import React, { useState } from 'react';
import { ChevronDown, ChevronUp, BarChart3 } from 'lucide-react';
import './ExpandableSection.css';

export default function ExpandableSection({ title, icon: Icon = BarChart3, children, defaultExpanded = false }) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <div className={`expandable-section ${isExpanded ? 'expanded' : ''}`}>
      <button 
        className="expandable-header"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="expandable-title">
          {Icon && <Icon size={20} />}
          <span>{title}</span>
        </div>
        {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
      </button>
      
      {isExpanded && (
        <div className="expandable-content">
          {children}
        </div>
      )}
    </div>
  );
}

