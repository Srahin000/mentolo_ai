import React from 'react';
import { Brain, Lightbulb, HelpCircle, TrendingUp } from 'lucide-react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer } from 'recharts';

export default function CognitivePatterns({ sessions = [], childName = 'Your child' }) {
  // Process cognitive data
  const cognitiveData = React.useMemo(() => {
    if (!sessions || sessions.length === 0) return null;

    const recentSessions = sessions.slice(-10);
    
    // Aggregate cognitive metrics
    let totalReasoning = 0;
    let totalAbstract = 0;
    let totalCuriosity = 0;
    let count = 0;

    recentSessions.forEach(session => {
      const analysis = session.analysis || {};
      const cognitive = analysis.cognitive_indicators || {};
      
      // Extract cognitive metrics - check multiple locations
      totalReasoning += session.reasoning_language_count 
        || analysis.reasoning_language_count 
        || (cognitive.reasoning_language ? (Array.isArray(cognitive.reasoning_language) ? cognitive.reasoning_language.length : cognitive.reasoning_language) : 0)
        || 0;
      totalAbstract += session.abstract_thinking_score 
        || analysis.abstract_thinking_score 
        || cognitive.abstract_thinking_score 
        || 0;
      totalCuriosity += session.curiosity_score 
        || analysis.curiosity_score 
        || cognitive.curiosity_score 
        || 0;
      count++;
    });

    const avgReasoning = count > 0 ? totalReasoning / count : 0;
    const avgAbstract = count > 0 ? totalAbstract / count : 0;
    const avgCuriosity = count > 0 ? totalCuriosity / count : 0;

    // Prepare radar chart data
    const radarData = [
      {
        category: 'Reasoning',
        value: Math.min(avgReasoning * 10, 100), // Scale to 0-100
        fullMark: 100
      },
      {
        category: 'Abstract Thinking',
        value: Math.min(avgAbstract, 100),
        fullMark: 100
      },
      {
        category: 'Curiosity',
        value: Math.min(avgCuriosity, 100),
        fullMark: 100
      }
    ];

    return {
      radarData,
      metrics: {
        reasoning: avgReasoning.toFixed(1),
        abstract: avgAbstract.toFixed(0),
        curiosity: avgCuriosity.toFixed(0)
      }
    };
  }, [sessions]);

  if (!cognitiveData) {
    return (
      <div className="cognitive-patterns">
        <h3 className="section-title">
          <Brain className="icon" />
          Cognitive Patterns
        </h3>
        <p className="empty-state">No cognitive data available yet.</p>
      </div>
    );
  }

  return (
    <div className="cognitive-patterns">
      <h3 className="section-title">
        <Brain className="icon" />
        Cognitive Patterns
      </h3>

      {/* Summary Cards */}
      <div className="cognitive-summary">
        <div className="cognitive-card">
          <div className="cognitive-icon-wrapper">
            <Lightbulb className="cognitive-icon" />
          </div>
          <div className="cognitive-content">
            <div className="cognitive-value">{cognitiveData.metrics.reasoning}</div>
            <div className="cognitive-label">Reasoning Language</div>
            <div className="cognitive-desc">"because", "so", "if" usage</div>
          </div>
        </div>
        <div className="cognitive-card">
          <div className="cognitive-icon-wrapper">
            <Brain className="cognitive-icon" />
          </div>
          <div className="cognitive-content">
            <div className="cognitive-value">{cognitiveData.metrics.abstract}</div>
            <div className="cognitive-label">Abstract Thinking</div>
            <div className="cognitive-desc">Score /100</div>
          </div>
        </div>
        <div className="cognitive-card">
          <div className="cognitive-icon-wrapper">
            <HelpCircle className="cognitive-icon" />
          </div>
          <div className="cognitive-content">
            <div className="cognitive-value">{cognitiveData.metrics.curiosity}</div>
            <div className="cognitive-label">Curiosity Score</div>
            <div className="cognitive-desc">Based on question types</div>
          </div>
        </div>
      </div>

      {/* Radar Chart */}
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={300}>
          <RadarChart data={cognitiveData.radarData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="category" style={{ fontSize: '12px' }} />
            <PolarRadiusAxis angle={90} domain={[0, 100]} style={{ fontSize: '11px' }} />
            <Radar 
              name="Cognitive Skills" 
              dataKey="value" 
              stroke="#7B68EE" 
              fill="#7B68EE" 
              fillOpacity={0.6}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Insights */}
      <div className="cognitive-insights">
        {parseFloat(cognitiveData.metrics.curiosity) > 70 && (
          <div className="insight-badge positive">
            <HelpCircle size={16} />
            <span>{childName} shows strong curiosity! High curiosity scores indicate active learning and exploration.</span>
          </div>
        )}
        {parseFloat(cognitiveData.metrics.reasoning) > 5 && (
          <div className="insight-badge positive">
            <Lightbulb size={16} />
            <span>Great reasoning skills! Using causal language ("because", "so") shows logical thinking development.</span>
          </div>
        )}
        {parseFloat(cognitiveData.metrics.abstract) > 60 && (
          <div className="insight-badge positive">
            <Brain size={16} />
            <span>Strong abstract thinking! {childName} is developing the ability to think about concepts beyond concrete objects.</span>
          </div>
        )}
      </div>
    </div>
  );
}

