import React from 'react';
import { BookOpen, CheckCircle2, MessageSquare } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function LanguageDetails({ sessions = [], childName = 'Your child' }) {
  // Process language detail data
  const languageData = React.useMemo(() => {
    if (!sessions || sessions.length === 0) return null;

    const data = sessions
      .filter(s => s.analysis || s.grammar_accuracy !== undefined)
      .map((session, index) => {
        const analysis = session.analysis || {};
        const vocab = analysis.vocabulary_analysis || {};
        
        // Extract language metrics - check multiple locations
        const grammar = session.grammar_accuracy 
          || analysis.grammar_accuracy 
          || 0;
        const complexity = session.sentence_complexity 
          || analysis.sentence_complexity 
          || vocab.sentence_complexity 
          || 0;
        const vocabSize = session.vocabulary_size 
          || analysis.vocabulary_size 
          || vocab.vocabulary_size_estimate 
          || vocab.vocabulary_size 
          || 0;
        
        return {
          date: session.timestamp ? new Date(session.timestamp).toLocaleDateString() : `Session ${index + 1}`,
          grammar,
          complexity: complexity.toFixed(1),
          vocabSize
        };
      })
      .slice(-30);

    return data;
  }, [sessions]);

  // Calculate insights
  const insights = React.useMemo(() => {
    if (!languageData || languageData.length === 0) return null;

    const avgGrammar = languageData.reduce((sum, d) => sum + d.grammar, 0) / languageData.length;
    const avgComplexity = languageData.reduce((sum, d) => sum + parseFloat(d.complexity), 0) / languageData.length;
    const recentGrammar = languageData.slice(-5).reduce((sum, d) => sum + d.grammar, 0) / 5;
    const recentComplexity = languageData.slice(-5).reduce((sum, d) => sum + parseFloat(d.complexity), 0) / 5;

    return {
      avgGrammar: avgGrammar.toFixed(0),
      avgComplexity: avgComplexity.toFixed(1),
      recentGrammar: recentGrammar.toFixed(0),
      recentComplexity: recentComplexity.toFixed(1),
      grammarImproving: recentGrammar > avgGrammar * 1.05,
      complexityImproving: recentComplexity > avgComplexity * 1.05
    };
  }, [languageData]);

  if (!languageData || languageData.length === 0) {
    return (
      <div className="language-details">
        <h3 className="section-title">
          <BookOpen className="icon" />
          Language Details
        </h3>
        <p className="empty-state">No language detail data available yet.</p>
      </div>
    );
  }

  return (
    <div className="language-details">
      <h3 className="section-title">
        <BookOpen className="icon" />
        Language Details
      </h3>

      {/* Summary Stats */}
      {insights && (
        <div className="language-summary">
          <div className="detail-card">
            <CheckCircle2 className="detail-icon" />
            <div className="detail-content">
              <div className="detail-value">{insights.avgGrammar}%</div>
              <div className="detail-label">Grammar Accuracy</div>
              <div className="detail-trend">
                {insights.grammarImproving ? 'Improving' : 'Stable'}
              </div>
            </div>
          </div>
          <div className="detail-card">
            <MessageSquare className="detail-icon" />
            <div className="detail-content">
              <div className="detail-value">{insights.avgComplexity}</div>
              <div className="detail-label">Avg Words/Sentence</div>
              <div className="detail-trend">
                {insights.complexityImproving ? 'Improving' : 'Stable'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Chart */}
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={languageData}>
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
              dataKey="grammar" 
              stroke="#4A90E2" 
              strokeWidth={2}
              name="Grammar Accuracy (%)"
              dot={{ r: 3 }}
            />
            <Line 
              type="monotone" 
              dataKey="complexity" 
              stroke="#7B68EE" 
              strokeWidth={2}
              name="Sentence Complexity"
              dot={{ r: 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Insights */}
      {insights && (
        <div className="language-insights">
          {insights.grammarImproving && (
            <div className="insight-badge positive">
              <CheckCircle2 size={16} />
              <span>{childName}'s grammar is improving! Recent accuracy of {insights.recentGrammar}% shows great progress.</span>
            </div>
          )}
          {insights.complexityImproving && (
            <div className="insight-badge positive">
              <MessageSquare size={16} />
              <span>Sentence complexity is growing! {childName} is using longer, more detailed sentences.</span>
            </div>
          )}
          {insights.avgGrammar < 70 && (
            <div className="insight-badge opportunity">
              <BookOpen size={16} />
              <span>Grammar accuracy at {insights.avgGrammar}%. Practice with sentence structure activities to improve.</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

