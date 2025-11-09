/**
 * Cortex AI Insights Component
 * Displays AI-powered insights from Snowflake Cortex
 */

import React, { useState, useEffect } from 'react';
import { getCortexAnalysis } from '../services/api';
import { Sparkles, TrendingUp, Target, BarChart3, Loader2, AlertCircle } from 'lucide-react';
import './CortexInsights.css';

function CortexInsights({ childId }) {
  const [loading, setLoading] = useState(true);
  const [insights, setInsights] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('trends');

  useEffect(() => {
    loadInsights();
  }, [childId, activeTab]);

  const loadInsights = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const analysis = await getCortexAnalysis(childId, activeTab, 90);
      
      if (analysis.available) {
        setInsights(analysis);
      } else {
        setError(analysis.message || 'Cortex AI not available in this region');
      }
    } catch (err) {
      setError(err.message || 'Failed to load Cortex insights');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="cortex-insights-loading">
        <Loader2 className="spinner" />
        <p>Loading AI insights...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="cortex-insights-error">
        <AlertCircle size={20} />
        <p>{error}</p>
        <small>Using Gemini Pro fallback for analysis</small>
      </div>
    );
  }

  const analysis = insights?.analysis || {};
  const tabs = [
    { id: 'trends', label: 'Trends', icon: TrendingUp },
    { id: 'patterns', label: 'Patterns', icon: BarChart3 },
    { id: 'benchmarks', label: 'Benchmarks', icon: Target },
  ];

  return (
    <div className="cortex-insights">
      <div className="cortex-header">
        <div className="cortex-title">
          <Sparkles size={24} />
          <h2>AI-Powered Insights</h2>
          <span className="cortex-badge">Cortex AI</span>
        </div>
        <div className="cortex-tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`cortex-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <tab.icon size={16} />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <div className="cortex-content">
        {activeTab === 'trends' && (
          <div className="cortex-section">
            <h3>Development Trajectory</h3>
            <p className="cortex-text">{analysis.trajectory || 'Analyzing development trends...'}</p>
            
            {analysis.strengths && analysis.strengths.length > 0 && (
              <div className="cortex-strengths">
                <h4>Top Strengths</h4>
                {analysis.strengths.map((strength, idx) => (
                  <div key={idx} className="cortex-item">
                    <strong>{strength.area || strength.title}</strong>
                    <p>{strength.evidence || strength.why_matters}</p>
                  </div>
                ))}
              </div>
            )}

            {analysis.growth_areas && analysis.growth_areas.length > 0 && (
              <div className="cortex-growth">
                <h4>Growth Areas</h4>
                {analysis.growth_areas.map((area, idx) => (
                  <div key={idx} className="cortex-item">
                    <strong>{area.area || area.title}</strong>
                    <p>{area.next_step || area.recommendation}</p>
                  </div>
                ))}
              </div>
            )}

            {analysis.recommendations && (
              <div className="cortex-recommendations">
                <h4>Recommendations</h4>
                <ul>
                  {Array.isArray(analysis.recommendations) ? (
                    analysis.recommendations.map((rec, idx) => (
                      <li key={idx}>{rec}</li>
                    ))
                  ) : (
                    <li>{analysis.recommendations}</li>
                  )}
                </ul>
              </div>
            )}
          </div>
        )}

        {activeTab === 'patterns' && (
          <div className="cortex-section">
            <h3>Pattern Detection</h3>
            {analysis.patterns ? (
              <div className="cortex-patterns">
                {analysis.patterns.correlations && (
                  <div className="cortex-item">
                    <h4>Correlations</h4>
                    <p>{typeof analysis.patterns.correlations === 'string' 
                      ? analysis.patterns.correlations 
                      : JSON.stringify(analysis.patterns.correlations, null, 2)}</p>
                  </div>
                )}
                {analysis.patterns.temporal_patterns && (
                  <div className="cortex-item">
                    <h4>Temporal Patterns</h4>
                    <p>{typeof analysis.patterns.temporal_patterns === 'string' 
                      ? analysis.patterns.temporal_patterns 
                      : JSON.stringify(analysis.patterns.temporal_patterns, null, 2)}</p>
                  </div>
                )}
                {analysis.patterns.anomalies && (
                  <div className="cortex-item">
                    <h4>Anomalies</h4>
                    <p>{typeof analysis.patterns.anomalies === 'string' 
                      ? analysis.patterns.anomalies 
                      : JSON.stringify(analysis.patterns.anomalies, null, 2)}</p>
                  </div>
                )}
              </div>
            ) : (
              <p className="cortex-text">{analysis.raw_response || 'Analyzing patterns...'}</p>
            )}
          </div>
        )}

        {activeTab === 'benchmarks' && (
          <div className="cortex-section">
            <h3>Benchmark Comparison</h3>
            {analysis.comparison ? (
              <div className="cortex-benchmarks">
                {analysis.comparison.ahead_of_benchmark && (
                  <div className="cortex-item positive">
                    <h4>Ahead of Benchmark</h4>
                    <p>{typeof analysis.comparison.ahead_of_benchmark === 'string' 
                      ? analysis.comparison.ahead_of_benchmark 
                      : JSON.stringify(analysis.comparison.ahead_of_benchmark, null, 2)}</p>
                  </div>
                )}
                {analysis.comparison.on_track && (
                  <div className="cortex-item neutral">
                    <h4>On Track</h4>
                    <p>{typeof analysis.comparison.on_track === 'string' 
                      ? analysis.comparison.on_track 
                      : JSON.stringify(analysis.comparison.on_track, null, 2)}</p>
                  </div>
                )}
                {analysis.comparison.needs_support && (
                  <div className="cortex-item warning">
                    <h4>Needs Support</h4>
                    <p>{typeof analysis.comparison.needs_support === 'string' 
                      ? analysis.comparison.needs_support 
                      : JSON.stringify(analysis.comparison.needs_support, null, 2)}</p>
                  </div>
                )}
                {analysis.comparison.recommendations && (
                  <div className="cortex-recommendations">
                    <h4>Recommendations</h4>
                    <ul>
                      {Array.isArray(analysis.comparison.recommendations) ? (
                        analysis.comparison.recommendations.map((rec, idx) => (
                          <li key={idx}>{rec}</li>
                        ))
                      ) : (
                        <li>{analysis.comparison.recommendations}</li>
                      )}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <p className="cortex-text">{analysis.raw_response || 'Comparing to benchmarks...'}</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default CortexInsights;

