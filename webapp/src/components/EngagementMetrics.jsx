import React from 'react';
import { Clock, MessageCircle, Sparkles, TrendingUp } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function EngagementMetrics({ sessions = [], childName = 'Your child' }) {
  // Process engagement data from sessions
  const engagementData = React.useMemo(() => {
    if (!sessions || sessions.length === 0) return null;

    const data = sessions
      .filter(s => s.analysis || s.session_context)
      .map((session, index) => {
        const analysis = session.analysis || {};
        const context = session.session_context || {};
        
        // Extract engagement metrics - check multiple locations
        // session_duration is in seconds, convert to minutes
        let duration = 0;
        if (session.session_duration) {
          duration = session.session_duration / 60.0; // Convert seconds to minutes
        } else if (context.duration_minutes) {
          duration = context.duration_minutes;
        } else if (context.session_duration) {
          duration = context.session_duration / 60.0; // Convert seconds to minutes
        } else if (analysis.session_duration) {
          duration = analysis.session_duration / 60.0; // Convert seconds to minutes
        }
        const turns = session.conversation_turns 
          || analysis.conversation_turns 
          || context.conversation_turns 
          || 0;
        const childInitiated = session.child_initiated_topics 
          || analysis.child_initiated_topics 
          || context.child_initiated_topics 
          || 0;
        
        return {
          date: session.timestamp ? new Date(session.timestamp).toLocaleDateString() : `Session ${index + 1}`,
          duration: duration,
          turns: turns,
          childInitiated: childInitiated
        };
      })
      .slice(-30); // Last 30 sessions

    return data;
  }, [sessions]);

  // Calculate averages and insights
  const insights = React.useMemo(() => {
    if (!engagementData || engagementData.length === 0) return null;

    const avgDuration = engagementData.reduce((sum, d) => sum + (d.duration || 0), 0) / engagementData.length;
    const avgTurns = engagementData.reduce((sum, d) => sum + (d.turns || 0), 0) / engagementData.length;
    const avgInitiated = engagementData.reduce((sum, d) => sum + (d.childInitiated || 0), 0) / engagementData.length;
    const totalInitiated = engagementData.reduce((sum, d) => sum + (d.childInitiated || 0), 0);

    return {
      avgDuration: avgDuration.toFixed(1),
      avgTurns: avgTurns.toFixed(1),
      avgInitiated: avgInitiated.toFixed(1),
      totalInitiated,
      totalSessions: engagementData.length
    };
  }, [engagementData]);

  if (!engagementData || engagementData.length === 0) {
    return (
      <div className="engagement-metrics">
        <h3 className="section-title">
          <MessageCircle className="icon" />
          Engagement Metrics
        </h3>
        <p className="empty-state">No engagement data available yet.</p>
      </div>
    );
  }

  return (
    <div className="engagement-metrics">
      <h3 className="section-title">
        <MessageCircle className="icon" />
        Engagement Metrics
      </h3>

      {/* Summary Cards */}
      {insights && (
        <div className="engagement-summary">
          <div className="metric-card">
            <Clock className="metric-icon" />
            <div className="metric-content">
              <div className="metric-value">{insights.avgDuration}</div>
              <div className="metric-label">Avg Session (min)</div>
            </div>
          </div>
          <div className="metric-card">
            <MessageCircle className="metric-icon" />
            <div className="metric-content">
              <div className="metric-value">{insights.avgTurns}</div>
              <div className="metric-label">Avg Conversation Turns</div>
            </div>
          </div>
          <div className="metric-card">
            <Sparkles className="metric-icon" />
            <div className="metric-content">
              <div className="metric-value">{insights.totalInitiated}</div>
              <div className="metric-label">Topics {childName} Started</div>
            </div>
          </div>
        </div>
      )}

      {/* Engagement Chart */}
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={engagementData}>
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
            <Line 
              type="monotone" 
              dataKey="duration" 
              stroke="#4A90E2" 
              strokeWidth={2}
              name="Duration (min)"
              dot={{ r: 3 }}
            />
            <Line 
              type="monotone" 
              dataKey="turns" 
              stroke="#50C878" 
              strokeWidth={2}
              name="Conversation Turns"
              dot={{ r: 3 }}
            />
            <Line 
              type="monotone" 
              dataKey="childInitiated" 
              stroke="#FFB347" 
              strokeWidth={2}
              name="Child-Initiated Topics"
              dot={{ r: 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Insights */}
      {insights && (
        <div className="engagement-insights">
          {insights.avgInitiated > 2 && (
            <div className="insight-badge positive">
              <Sparkles size={16} />
              <span>{childName} is very engaged! Starting {insights.avgInitiated} topics per session shows strong initiative.</span>
            </div>
          )}
          {insights.avgTurns > 20 && (
            <div className="insight-badge positive">
              <MessageCircle size={16} />
              <span>Great conversation flow! {insights.avgTurns} turns per session indicates active participation.</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

