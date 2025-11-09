import React, { useState, useEffect } from 'react';
import { getChildProfile, getDashboard, getAnalyticsInsights } from './services/api';
import DailyInsightCard from './components/DailyInsightCard';
import CortexChatbot from './components/CortexChatbot';
import OverallGrowthScore from './components/OverallGrowthScore';
import ThisWeeksStrength from './components/ThisWeeksStrength';
import AreaToNurture from './components/AreaToNurture';
import SimpleNextStep from './components/SimpleNextStep';
import TimelineSneakPeek from './components/TimelineSneakPeek';
import ExpandableSection from './components/ExpandableSection';
import SuggestPlaces from './components/SuggestPlaces';
import DevelopmentSnapshotGrid from './components/DevelopmentSnapshotGrid';
import EngagementMetrics from './components/EngagementMetrics';
import EmotionalIntelligence from './components/EmotionalIntelligence';
import CognitivePatterns from './components/CognitivePatterns';
import LanguageDetails from './components/LanguageDetails';
import SpeechClarity from './components/SpeechClarity';
import CortexInsights from './components/CortexInsights';
import PlacesRecommendations from './components/PlacesRecommendations';
import { Loader2, RefreshCw, BarChart3, Brain, Heart, MessageSquare, Mic, MapPin, Sparkles } from 'lucide-react';
import './App.css';

function App() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [childData, setChildData] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [childId, setChildId] = useState('demo_child_tommy'); // Default to Tommy

  useEffect(() => {
    loadDashboardData();
  }, [childId]);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Load child profile
      const profileData = await getChildProfile(childId);
      setChildData(profileData);

      // Load dashboard data
      const dashData = await getDashboard(childId);
      setDashboardData(dashData);

      // Load analytics insights
      const insights = await getAnalyticsInsights(childId);
      if (insights && insights.insights) {
        // Merge insights into dashboard data
        setDashboardData(prev => ({
          ...prev,
          ai_insights: insights.insights,
        }));
      }
    } catch (err) {
      console.error('Error loading dashboard:', err);
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="app-loading">
        <Loader2 className="spinner" />
        <p>Loading dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app-error">
        <h2>Error Loading Dashboard</h2>
        <p>{error}</p>
        <button onClick={loadDashboardData} className="btn-primary">
          <RefreshCw size={16} /> Retry
        </button>
      </div>
    );
  }

  // Extract data from child profile
  const profile = childData?.profile || {};
  const sessions = childData?.sessions || [];
  const trends = childData?.trends || {};
  const latestSession = sessions[sessions.length - 1];
  
  // Get daily insight from latest session or dashboard
  const dailyInsight = latestSession?.analysis?.daily_insight 
    || dashboardData?.ai_insights?.[0]
    || "Start a conversation to see insights!";

  // Get development snapshot - build from enriched columns if analysis doesn't have it
  let developmentSnapshot = latestSession?.analysis?.development_snapshot || {};
  
  // If snapshot is empty but we have enriched columns, build it from direct properties
  if (!developmentSnapshot || Object.keys(developmentSnapshot).length === 0) {
    if (latestSession) {
      // Use enriched columns from Snowflake
      const langScore = latestSession.language_score || 0;
      const cogScore = latestSession.cognitive_score || 0;
      const emoScore = latestSession.emotional_score || 0;
      const socScore = latestSession.social_score || 0;
      const creScore = latestSession.creativity_score || 0;
      
      developmentSnapshot = {
        language: {
          score: langScore,
          level: langScore >= 80 ? 'strong' : (langScore >= 60 ? 'growing' : (langScore > 0 ? 'developing' : 'Not assessed'))
        },
        cognitive: {
          score: cogScore,
          level: cogScore >= 80 ? 'strong' : (cogScore >= 60 ? 'growing' : (cogScore > 0 ? 'developing' : 'Not assessed'))
        },
        emotional: {
          score: emoScore,
          level: emoScore >= 80 ? 'strong' : (emoScore >= 60 ? 'growing' : (emoScore > 0 ? 'developing' : 'Not assessed'))
        },
        social: {
          score: socScore,
          level: socScore >= 80 ? 'strong' : (socScore >= 60 ? 'growing' : (socScore > 0 ? 'developing' : 'Not assessed'))
        },
        creativity: {
          score: creScore,
          level: creScore >= 80 ? 'strong' : (creScore >= 60 ? 'growing' : (creScore > 0 ? 'developing' : 'Not assessed'))
        },
        physical: {
          score: 0, // Physical score not tracked yet
          level: 'Not assessed'
        }
      };
    } else if (sessions.length > 0) {
      // Calculate averages from all sessions
      const avgLang = sessions.reduce((sum, s) => sum + (s.language_score || 0), 0) / sessions.length;
      const avgCog = sessions.reduce((sum, s) => sum + (s.cognitive_score || 0), 0) / sessions.length;
      const avgEmo = sessions.reduce((sum, s) => sum + (s.emotional_score || 0), 0) / sessions.length;
      const avgSoc = sessions.reduce((sum, s) => sum + (s.social_score || 0), 0) / sessions.length;
      const avgCre = sessions.reduce((sum, s) => sum + (s.creativity_score || 0), 0) / sessions.length;
      
      developmentSnapshot = {
        language: {
          score: Math.round(avgLang),
          level: avgLang >= 80 ? 'strong' : (avgLang >= 60 ? 'growing' : (avgLang > 0 ? 'developing' : 'Not assessed'))
        },
        cognitive: {
          score: Math.round(avgCog),
          level: avgCog >= 80 ? 'strong' : (avgCog >= 60 ? 'growing' : (avgCog > 0 ? 'developing' : 'Not assessed'))
        },
        emotional: {
          score: Math.round(avgEmo),
          level: avgEmo >= 80 ? 'strong' : (avgEmo >= 60 ? 'growing' : (avgEmo > 0 ? 'developing' : 'Not assessed'))
        },
        social: {
          score: Math.round(avgSoc),
          level: avgSoc >= 80 ? 'strong' : (avgSoc >= 60 ? 'growing' : (avgSoc > 0 ? 'developing' : 'Not assessed'))
        },
        creativity: {
          score: Math.round(avgCre),
          level: avgCre >= 80 ? 'strong' : (avgCre >= 60 ? 'growing' : (avgCre > 0 ? 'developing' : 'Not assessed'))
        },
        physical: {
          score: 0,
          level: 'Not assessed'
        }
      };
    }
  }

  // Get strengths and growth areas
  const strengths = latestSession?.analysis?.strengths || [];
  const growthAreas = latestSession?.analysis?.growth_opportunities || [];
  const activities = latestSession?.analysis?.personalized_activities || [];

  // Calculate overall growth score and trend
  let overallScore = 0;
  let trend = 0;
  if (sessions.length > 0) {
    // Calculate average score from all sessions
    const scores = sessions
      .filter(s => s.language_score || s.cognitive_score || s.emotional_score)
      .map(s => {
        const lang = s.language_score || 0;
        const cog = s.cognitive_score || 0;
        const emo = s.emotional_score || 0;
        const soc = s.social_score || 0;
        const cre = s.creativity_score || 0;
        return (lang + cog + emo + soc + cre) / 5;
      });
    
    if (scores.length > 0) {
      overallScore = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
      
      // Calculate trend (compare recent vs older sessions)
      if (scores.length >= 4) {
        const recent = scores.slice(-2).reduce((a, b) => a + b, 0) / 2;
        const older = scores.slice(0, 2).reduce((a, b) => a + b, 0) / 2;
        trend = recent - older;
      }
    }
  }

  // Get top strength (first one)
  const topStrength = strengths.length > 0 ? strengths[0] : null;

  // Get top growth area (first one)
  const topGrowthArea = growthAreas.length > 0 ? growthAreas[0] : null;

  // Get next activity (first one)
  const nextActivity = activities.length > 0 ? activities[0] : null;

  const childName = profile.name || profile.child_name || 'Your child';
  const childAge = profile.age || profile.child_age || 4;

  return (
    <div className="app">
      <header className="app-header">
        <h1>Curiosity Companion Dashboard</h1>
        <div className="header-actions">
          <input
            type="text"
            placeholder="Child ID"
            value={childId}
            onChange={(e) => setChildId(e.target.value)}
            className="child-id-input"
          />
          <button onClick={loadDashboardData} className="btn-refresh">
            <RefreshCw size={16} /> Refresh
          </button>
        </div>
      </header>

      <main className="dashboard-container simplified-dashboard">
        {/* Daily Insight Card - Full Width */}
        <div className="full-width-section">
          <DailyInsightCard insight={dailyInsight} childName={childName} />
        </div>

        {/* Cortex Chatbot - Full Width */}
        <div className="full-width-section">
          <CortexChatbot childId={childId} childName={childName} />
        </div>

        {/* Two-Column Grid for Main Content */}
        <div className="two-column-grid">
          {/* Overall Growth Score */}
          <OverallGrowthScore 
            score={overallScore} 
            trend={trend} 
            sessions={sessions} 
          />

          {/* Timeline Sneak Peek */}
          <TimelineSneakPeek sessions={sessions} childName={childName} />
        </div>

        <div className="two-column-grid">
          {/* This Week's Strength */}
          <ThisWeeksStrength strength={topStrength} childName={childName} />

          {/* Area to Nurture */}
          <AreaToNurture growthArea={topGrowthArea} childName={childName} />
        </div>

        {/* Simple Next Step - Full Width */}
        <div className="full-width-section">
          <SimpleNextStep activity={nextActivity} />
        </div>

        {/* Suggest Places - Expandable */}
        <div className="full-width-section">
          <SuggestPlaces childId={childId} childName={childName} />
        </div>

        {/* Expandable Detailed Sections */}
        <div className="expandable-sections">
          <ExpandableSection 
            title="Development Snapshot" 
            icon={BarChart3}
          >
            <DevelopmentSnapshotGrid snapshot={developmentSnapshot} />
          </ExpandableSection>

          <ExpandableSection 
            title="Engagement & Activity Metrics" 
            icon={BarChart3}
          >
            <EngagementMetrics sessions={sessions} childName={childName} />
          </ExpandableSection>

          <ExpandableSection 
            title="Emotional Intelligence" 
            icon={Heart}
          >
            <EmotionalIntelligence sessions={sessions} childName={childName} />
          </ExpandableSection>

          <ExpandableSection 
            title="Cognitive Patterns" 
            icon={Brain}
          >
            <CognitivePatterns sessions={sessions} childName={childName} />
          </ExpandableSection>

          <ExpandableSection 
            title="Language Details" 
            icon={MessageSquare}
          >
            <LanguageDetails sessions={sessions} childName={childName} />
          </ExpandableSection>

          <ExpandableSection 
            title="Speech Clarity" 
            icon={Mic}
          >
            <SpeechClarity sessions={sessions} childName={childName} />
          </ExpandableSection>

          <ExpandableSection 
            title="AI-Powered Insights (Cortex)" 
            icon={Sparkles}
          >
            <CortexInsights childId={childId} />
          </ExpandableSection>
        </div>
      </main>

      <footer className="app-footer">
        <p>Curiosity Companion - AI-Powered Child Development Dashboard</p>
      </footer>
    </div>
  );
}

export default App;
