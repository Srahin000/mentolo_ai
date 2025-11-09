import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown, ArrowUp, ArrowDown } from 'lucide-react';

export default function GrowthTimelineChart({ trends = {}, childAge = 4, childName = 'Your child' }) {
  // Transform trends data for chart
  const chartData = React.useMemo(() => {
    const vocabulary = trends.vocabulary_growth || [];
    const complexity = trends.complexity_progression || [];
    
    // Combine data by date
    const dateMap = new Map();
    
    vocabulary.forEach((item, index) => {
      const date = item.date || `Day ${index + 1}`;
      if (!dateMap.has(date)) {
        dateMap.set(date, { date });
      }
      dateMap.get(date).vocabulary = item.value || item;
    });
    
    complexity.forEach((item, index) => {
      const date = item.date || `Day ${index + 1}`;
      if (!dateMap.has(date)) {
        dateMap.set(date, { date });
      }
      dateMap.get(date).complexity = item.value || item;
    });
    
    return Array.from(dateMap.values()).slice(-30); // Last 30 days
  }, [trends]);

  // Calculate insights from chart data
  const insights = React.useMemo(() => {
    if (chartData.length < 2) return null;

    const vocabValues = chartData.map(d => d.vocabulary).filter(v => v !== undefined);
    const complexityValues = chartData.map(d => d.complexity).filter(v => v !== undefined);

    const insightsList = [];

    // Vocabulary trend
    if (vocabValues.length >= 2) {
      const firstVocab = vocabValues[0];
      const lastVocab = vocabValues[vocabValues.length - 1];
      const vocabChange = lastVocab - firstVocab;
      const vocabPercentChange = firstVocab > 0 ? ((vocabChange / firstVocab) * 100).toFixed(1) : 0;
      
      // Calculate trend direction
      const vocabTrend = vocabChange > 0 ? 'up' : vocabChange < 0 ? 'down' : 'stable';
      
      insightsList.push({
        metric: 'Vocabulary',
        current: lastVocab,
        change: vocabChange,
        percentChange: vocabPercentChange,
        trend: vocabTrend,
        message: vocabTrend === 'up' 
          ? `Growing! ${childName} has added ${Math.abs(vocabChange)} words (${Math.abs(vocabPercentChange)}% increase)`
          : vocabTrend === 'down'
          ? `Declined by ${Math.abs(vocabChange)} words`
          : 'Stable vocabulary level'
      });
    }

    // Complexity trend
    if (complexityValues.length >= 2) {
      const firstComplexity = complexityValues[0];
      const lastComplexity = complexityValues[complexityValues.length - 1];
      const complexityChange = lastComplexity - firstComplexity;
      
      // Age-appropriate benchmarks
      const ageBenchmarks = {
        3: 3.5,
        4: 4.5,
        5: 5.5,
        6: 6.0
      };
      const benchmark = ageBenchmarks[childAge] || 4.5;
      const isOnTrack = lastComplexity >= benchmark * 0.8;
      
      const complexityTrend = complexityChange > 0.1 ? 'up' : complexityChange < -0.1 ? 'down' : 'stable';
      
      insightsList.push({
        metric: 'Sentence Complexity',
        current: lastComplexity.toFixed(1),
        change: complexityChange.toFixed(1),
        trend: complexityTrend,
        benchmark: benchmark,
        isOnTrack: isOnTrack,
        message: isOnTrack
          ? `On track! ${lastComplexity.toFixed(1)} words/sentence (target: ${benchmark})`
          : `Opportunity: ${lastComplexity.toFixed(1)} words/sentence (target: ${benchmark})`
      });
    }

    return insightsList;
  }, [chartData, childAge, childName]);

  if (chartData.length === 0) {
    return (
      <div className="growth-timeline">
        <h3 className="section-title">
          <TrendingUp className="icon" />
          Growth Timeline (Past 30 Days)
        </h3>
        <p className="empty-state">No data available yet. Start tracking progress!</p>
      </div>
    );
  }

  return (
    <div className="growth-timeline">
      <h3 className="section-title">
        <TrendingUp className="icon" />
        Growth Timeline (Past 30 Days)
      </h3>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis 
              dataKey="date" 
              stroke="#666"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#666"
              style={{ fontSize: '12px' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#fff', 
                border: '1px solid #ddd',
                borderRadius: '8px'
              }}
            />
            <Legend />
            {chartData.some(d => d.vocabulary !== undefined) && (
              <Line 
                type="monotone" 
                dataKey="vocabulary" 
                stroke="#4A90E2" 
                strokeWidth={2}
                name="Vocabulary"
                dot={{ r: 4 }}
              />
            )}
            {chartData.some(d => d.complexity !== undefined) && (
              <Line 
                type="monotone" 
                dataKey="complexity" 
                stroke="#7B68EE" 
                strokeWidth={2}
                name="Sentence Complexity"
                dot={{ r: 4 }}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      {/* Enhanced Insights Section */}
      {insights && insights.length > 0 && (
        <div className="timeline-insights">
          <h4 className="insights-title">Trend Analysis</h4>
          <div className="insights-grid">
            {insights.map((insight, index) => (
              <div key={index} className={`trend-card trend-${insight.trend}`}>
                <div className="trend-header">
                  <h5>{insight.metric}</h5>
                  {insight.trend === 'up' && <ArrowUp className="trend-icon up" />}
                  {insight.trend === 'down' && <ArrowDown className="trend-icon down" />}
                  {insight.trend === 'stable' && <TrendingUp className="trend-icon stable" />}
                </div>
                <div className="trend-stats">
                  <div className="trend-current">
                    <span className="trend-value">{insight.current}</span>
                    {insight.metric === 'Vocabulary' && <span className="trend-unit">words</span>}
                    {insight.metric === 'Sentence Complexity' && <span className="trend-unit">words/sentence</span>}
                  </div>
                  {insight.change !== undefined && insight.change !== '0.0' && (
                    <div className={`trend-change ${insight.trend}`}>
                      {insight.change > 0 ? '+' : ''}{insight.change}
                      {insight.percentChange && ` (${insight.percentChange}%)`}
                    </div>
                  )}
                  {insight.benchmark && (
                    <div className="trend-benchmark">
                      Age target: {insight.benchmark}
                    </div>
                  )}
                </div>
                <p className="trend-message">{insight.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {trends.insight && (
        <div className="timeline-insight">
          <p><strong>Insight:</strong> {trends.insight}</p>
        </div>
      )}
    </div>
  );
}

