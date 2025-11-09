import React from 'react';
import { Lightbulb, TrendingUp, TrendingDown, Target, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function InsightsPanel({ trends = {}, statistics = {}, childAge = 4, childName = 'Your child' }) {
  // Calculate insights from trends data
  const insights = React.useMemo(() => {
    if (!trends || !statistics) return null;

    const vocabularyData = trends.vocabulary_growth || [];
    const complexityData = trends.complexity_progression || [];
    
    const insightsList = [];

    // Vocabulary insights
    if (vocabularyData.length >= 2) {
      const firstVocab = vocabularyData[0]?.value || vocabularyData[0] || 0;
      const lastVocab = vocabularyData[vocabularyData.length - 1]?.value || vocabularyData[vocabularyData.length - 1] || 0;
      const vocabGrowth = lastVocab - firstVocab;
      const vocabGrowthPercent = firstVocab > 0 ? ((vocabGrowth / firstVocab) * 100).toFixed(1) : 0;

      if (vocabGrowth > 0) {
        insightsList.push({
          type: 'positive',
          icon: TrendingUp,
          title: 'Vocabulary Growth',
          message: `${childName} has added ${vocabGrowth} new words (${vocabGrowthPercent}% increase) in the past 30 days!`,
          detail: `Current vocabulary: ~${lastVocab} words. This is excellent progress for a ${childAge}-year-old.`,
          action: 'Keep reading together and introducing new words in context.'
        });
      } else if (vocabGrowth < 0) {
        insightsList.push({
          type: 'warning',
          icon: AlertCircle,
          title: 'Vocabulary Plateau',
          message: `Vocabulary growth has slowed. This is normal, but we can help accelerate it.`,
          detail: `Current vocabulary: ~${lastVocab} words.`,
          action: 'Try introducing more complex books and having deeper conversations.'
        });
      }
    }

    // Sentence complexity insights
    if (complexityData.length >= 2) {
      const firstComplexity = complexityData[0]?.value || complexityData[0] || 0;
      const lastComplexity = complexityData[complexityData.length - 1]?.value || complexityData[complexityData.length - 1] || 0;
      const complexityChange = lastComplexity - firstComplexity;

      // Age-appropriate benchmarks (words per sentence)
      const ageBenchmarks = {
        3: 3.5,
        4: 4.5,
        5: 5.5,
        6: 6.0
      };
      const benchmark = ageBenchmarks[childAge] || 4.5;

      if (lastComplexity < benchmark * 0.8) {
        insightsList.push({
          type: 'opportunity',
          icon: Target,
          title: 'Sentence Complexity Opportunity',
          message: `${childName}'s sentences average ${lastComplexity.toFixed(1)} words. The typical ${childAge}-year-old uses ${benchmark} words per sentence.`,
          detail: `This is a great area to focus on! Encourage longer, more detailed sentences.`,
          action: 'Ask "why" and "how" questions that require longer answers. Model complex sentences.'
        });
      } else if (lastComplexity >= benchmark) {
        insightsList.push({
          type: 'positive',
          icon: CheckCircle2,
          title: 'Strong Sentence Development',
          message: `${childName} is using ${lastComplexity.toFixed(1)} words per sentence, which is age-appropriate!`,
          detail: `This shows strong language development. Keep encouraging detailed storytelling.`,
          action: 'Continue reading together and asking open-ended questions.'
        });
      }
    }

    // Overall trend insights
    if (statistics.vocabulary_growth && statistics.vocabulary_growth > 50) {
      insightsList.push({
        type: 'positive',
        icon: TrendingUp,
        title: 'Rapid Vocabulary Expansion',
        message: `${childName} is learning new words at an impressive rate!`,
        detail: `This rapid growth suggests strong engagement and curiosity.`,
        action: 'Continue exposing them to rich language through books, conversations, and experiences.'
      });
    }

    // Question frequency insights
    if (statistics.question_frequency) {
      const avgQuestions = statistics.question_frequency;
      if (avgQuestions > 10) {
        insightsList.push({
          type: 'positive',
          icon: Lightbulb,
          title: 'Curious Mind',
          message: `${childName} asks an average of ${avgQuestions} questions per session!`,
          detail: `High question frequency indicates strong curiosity and cognitive engagement.`,
          action: 'Keep answering their questions thoughtfully and ask follow-up questions to deepen their thinking.'
        });
      }
    }

    return insightsList;
  }, [trends, statistics, childAge, childName]);

  if (!insights || insights.length === 0) {
    return (
      <div className="insights-panel">
        <h3 className="section-title">
          <Lightbulb className="icon" />
          Development Insights
        </h3>
        <p className="empty-state">No insights available yet. Keep tracking progress!</p>
      </div>
    );
  }

  return (
    <div className="insights-panel">
      <h3 className="section-title">
        <Lightbulb className="icon" />
        Development Insights
      </h3>
      <div className="insights-list">
        {insights.map((insight, index) => {
          const Icon = insight.icon;
          return (
            <div key={index} className={`insight-card insight-${insight.type}`}>
              <div className="insight-header">
                <div className="insight-icon-wrapper">
                  <Icon className="insight-icon" />
                </div>
                <h4 className="insight-title">{insight.title}</h4>
              </div>
              <p className="insight-message">{insight.message}</p>
              {insight.detail && (
                <p className="insight-detail">{insight.detail}</p>
              )}
              {insight.action && (
                <div className="insight-action">
                  <strong>Action:</strong> {insight.action}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

