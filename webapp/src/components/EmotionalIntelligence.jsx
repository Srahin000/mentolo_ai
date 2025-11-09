import React from 'react';
import { Heart, Smile, Users } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

export default function EmotionalIntelligence({ sessions = [], childName = 'Your child' }) {
  // Process emotional intelligence data
  const emotionalData = React.useMemo(() => {
    if (!sessions || sessions.length === 0) return null;

    const data = sessions
      .filter(s => s.analysis || s.emotional_score !== undefined)
      .map((session, index) => {
        const analysis = session.analysis || {};
        const emotionalIntel = analysis.emotional_intelligence || {};
        
        // Extract emotional intelligence metrics - check multiple locations
        const emotionWords = session.emotion_words_used 
          || analysis.emotion_words_used 
          || (emotionalIntel.emotion_words_used ? (Array.isArray(emotionalIntel.emotion_words_used) ? emotionalIntel.emotion_words_used.length : emotionalIntel.emotion_words_used) : 0)
          || 0;
        const empathyIndicators = session.empathy_indicators 
          || analysis.empathy_indicators 
          || (emotionalIntel.empathy_indicators ? (Array.isArray(emotionalIntel.empathy_indicators) ? emotionalIntel.empathy_indicators.length : emotionalIntel.empathy_indicators) : 0)
          || 0;
        const emotionalScore = session.emotional_score 
          || analysis.development_snapshot?.emotional?.score 
          || analysis.emotional_score 
          || 0;
        
        return {
          date: session.timestamp ? new Date(session.timestamp).toLocaleDateString() : `Session ${index + 1}`,
          emotionWords,
          empathyIndicators,
          emotionalScore
        };
      })
      .slice(-30);

    return data;
  }, [sessions]);

  // Calculate insights
  const insights = React.useMemo(() => {
    if (!emotionalData || emotionalData.length === 0) return null;

    const totalEmotionWords = emotionalData.reduce((sum, d) => sum + d.emotionWords, 0);
    const totalEmpathy = emotionalData.reduce((sum, d) => sum + d.empathyIndicators, 0);
    const avgEmotionalScore = emotionalData.reduce((sum, d) => sum + d.emotionalScore, 0) / emotionalData.length;
    const recentEmotionWords = emotionalData.slice(-5).reduce((sum, d) => sum + d.emotionWords, 0) / 5;
    const recentEmpathy = emotionalData.slice(-5).reduce((sum, d) => sum + d.empathyIndicators, 0) / 5;

    return {
      totalEmotionWords,
      totalEmpathy,
      avgEmotionalScore: avgEmotionalScore.toFixed(0),
      recentEmotionWords: recentEmotionWords.toFixed(1),
      recentEmpathy: recentEmpathy.toFixed(1),
      isGrowing: recentEmotionWords > (totalEmotionWords / emotionalData.length) * 1.1
    };
  }, [emotionalData]);

  if (!emotionalData || emotionalData.length === 0) {
    return (
      <div className="emotional-intelligence">
        <h3 className="section-title">
          <Heart className="icon" />
          Emotional Intelligence
        </h3>
        <p className="empty-state">No emotional intelligence data available yet.</p>
      </div>
    );
  }

  return (
    <div className="emotional-intelligence">
      <h3 className="section-title">
        <Heart className="icon" />
        Emotional Intelligence
      </h3>

      {/* Summary Stats */}
      {insights && (
        <div className="emotional-summary">
          <div className="stat-card">
            <Smile className="stat-icon" />
            <div className="stat-content">
              <div className="stat-value">{insights.totalEmotionWords}</div>
              <div className="stat-label">Emotion Words Used</div>
              <div className="stat-trend">
                Recent: {insights.recentEmotionWords} per session
              </div>
            </div>
          </div>
          <div className="stat-card">
            <Users className="stat-icon" />
            <div className="stat-content">
              <div className="stat-value">{insights.totalEmpathy}</div>
              <div className="stat-label">Empathy Indicators</div>
              <div className="stat-trend">
                Recent: {insights.recentEmpathy} per session
              </div>
            </div>
          </div>
          <div className="stat-card">
            <Heart className="stat-icon" />
            <div className="stat-content">
              <div className="stat-value">{insights.avgEmotionalScore}</div>
              <div className="stat-label">Emotional Score</div>
              <div className="stat-trend">/100</div>
            </div>
          </div>
        </div>
      )}

      {/* Chart */}
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={emotionalData.slice(-10)}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis 
              dataKey="date" 
              stroke="#666"
              style={{ fontSize: '11px' }}
              angle={-45}
              textAnchor="end"
              height={60}
            />
            <YAxis stroke="#666" style={{ fontSize: '12px' }} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#fff', 
                border: '1px solid #ddd',
                borderRadius: '8px'
              }}
            />
            <Legend />
            <Bar dataKey="emotionWords" fill="#FF6B9D" name="Emotion Words" />
            <Bar dataKey="empathyIndicators" fill="#50C878" name="Empathy Indicators" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Insights */}
      {insights && (
        <div className="emotional-insights">
          {insights.isGrowing && (
            <div className="insight-badge positive">
              <TrendingUp size={16} />
              <span>{childName}'s emotional vocabulary is growing! Using more emotion words shows developing self-awareness.</span>
            </div>
          )}
          {insights.recentEmpathy > 1 && (
            <div className="insight-badge positive">
              <Users size={16} />
              <span>Strong empathy skills! {childName} is recognizing and responding to others' emotions.</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

