import React from 'react';
import { Mic, Volume2, Target } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function SpeechClarity({ sessions = [], childName = 'Your child' }) {
  // Process speech clarity data
  const speechData = React.useMemo(() => {
    if (!sessions || sessions.length === 0) return null;

    const data = sessions
      .filter(s => s.analysis || s.speech_clarity_score !== undefined)
      .map((session, index) => {
        const analysis = session.analysis || {};
        const speech = analysis.speech_clarity || {};
        
        // Extract speech clarity metrics - check multiple locations
        const clarity = session.speech_clarity_score 
          || analysis.speech_clarity_score 
          || speech.intelligibility 
          || speech.speech_clarity_score 
          || 0;
        const soundsToPractice = session.sounds_to_practice 
          || analysis.sounds_to_practice 
          || speech.sounds_to_practice 
          || [];
        
        return {
          date: session.timestamp ? new Date(session.timestamp).toLocaleDateString() : `Session ${index + 1}`,
          clarity,
          soundsCount: Array.isArray(soundsToPractice) ? soundsToPractice.length : 0
        };
      })
      .slice(-30);

    return data;
  }, [sessions]);

  // Get sounds to practice from latest session
  const soundsToPractice = React.useMemo(() => {
    if (!sessions || sessions.length === 0) return [];
    
    const latest = sessions[sessions.length - 1];
    const analysis = latest?.analysis || {};
    const speech = analysis.speech_clarity || {};
    
    return latest?.sounds_to_practice 
      || analysis.sounds_to_practice 
      || speech.sounds_to_practice 
      || [];
  }, [sessions]);

  // Calculate insights
  const insights = React.useMemo(() => {
    if (!speechData || speechData.length === 0) return null;

    const avgClarity = speechData.reduce((sum, d) => sum + d.clarity, 0) / speechData.length;
    const recentClarity = speechData.slice(-5).reduce((sum, d) => sum + d.clarity, 0) / 5;
    const isImproving = recentClarity > avgClarity * 1.02;

    return {
      avgClarity: avgClarity.toFixed(0),
      recentClarity: recentClarity.toFixed(0),
      isImproving,
      level: avgClarity >= 90 ? 'Excellent' : avgClarity >= 80 ? 'Good' : avgClarity >= 70 ? 'Developing' : 'Needs Practice'
    };
  }, [speechData]);

  if (!speechData || speechData.length === 0) {
    return (
      <div className="speech-clarity">
        <h3 className="section-title">
          <Mic className="icon" />
          Speech Clarity
        </h3>
        <p className="empty-state">No speech clarity data available yet.</p>
      </div>
    );
  }

  return (
    <div className="speech-clarity">
      <h3 className="section-title">
        <Mic className="icon" />
        Speech Clarity
      </h3>

      {/* Summary Card */}
      {insights && (
        <div className="speech-summary">
          <div className="speech-card">
            <Volume2 className="speech-icon" />
            <div className="speech-content">
              <div className="speech-value">{insights.avgClarity}%</div>
              <div className="speech-label">Speech Intelligibility</div>
              <div className="speech-level">{insights.level}</div>
              {insights.isImproving && (
                <div className="speech-trend positive">Improving</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Chart */}
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={speechData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis 
              dataKey="date" 
              stroke="#666"
              style={{ fontSize: '11px' }}
              angle={-45}
              textAnchor="end"
              height={60}
            />
            <YAxis 
              stroke="#666" 
              style={{ fontSize: '12px' }}
              domain={[0, 100]}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#fff', 
                border: '1px solid #ddd',
                borderRadius: '8px'
              }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="clarity" 
              stroke="#50C878" 
              strokeWidth={2}
              name="Speech Clarity (%)"
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Sounds to Practice */}
      {soundsToPractice && soundsToPractice.length > 0 && (
        <div className="sounds-practice">
          <h4 className="sounds-title">
            <Target className="sounds-icon" />
            Sounds to Practice
          </h4>
          <div className="sounds-list">
            {soundsToPractice.map((sound, index) => (
              <div key={index} className="sound-badge">
                {sound}
              </div>
            ))}
          </div>
          <p className="sounds-note">
            Practice these sounds through fun games and activities!
          </p>
        </div>
      )}

      {/* Insights */}
      {insights && (
        <div className="speech-insights">
          {insights.avgClarity >= 90 && (
            <div className="insight-badge positive">
              <Volume2 size={16} />
              <span>Excellent speech clarity! {childName}'s speech is very clear and easy to understand.</span>
            </div>
          )}
          {insights.avgClarity < 80 && insights.avgClarity >= 70 && (
            <div className="insight-badge opportunity">
              <Target size={16} />
              <span>Speech clarity is developing. Continue practicing clear pronunciation through reading and conversation.</span>
            </div>
          )}
          {insights.avgClarity < 70 && (
            <div className="insight-badge warning">
              <Mic size={16} />
              <span>Focus on speech clarity. Practice sounds through fun activities and consider speech therapy if needed.</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

