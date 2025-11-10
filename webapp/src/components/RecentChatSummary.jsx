/**
 * Recent Chat Summary Component
 * Displays a one-line summary of recent chat sessions analyzed by Gemini Pro
 * Includes transcript to verify the insight
 */

import React, { useState } from 'react';
import { MessageSquare, ChevronDown, ChevronUp, FileText } from 'lucide-react';
import './RecentChatSummary.css';

export default function RecentChatSummary({ recentChatAnalysis, childName = 'Your child' }) {
  const [showTranscript, setShowTranscript] = useState(false);

  if (!recentChatAnalysis || Object.keys(recentChatAnalysis).length === 0) {
    return null;
  }

  const {
    recent_sessions = [],
    aggregated_insights = [],
    total_sessions_analyzed = 0
  } = recentChatAnalysis;

  // Get the most recent session - ensure insight and transcript are from the same session
  const mostRecentSession = recent_sessions.length > 0 ? recent_sessions[0] : null;
  
  // Only use the insight if we have the matching transcript from the same session
  // This ensures the insight matches what was actually said
  const summaryText = mostRecentSession?.daily_insight || null;
  const transcript = mostRecentSession?.transcript || '';
  const backendDetectedMismatch = mostRecentSession?.insight_matches_transcript === false;
  
  // If no insight from most recent session, don't show anything to avoid mismatches
  if (!summaryText) {
    return null;
  }
  
  // Check if insight seems to match transcript content (frontend validation as backup)
  const transcriptLower = transcript.toLowerCase();
  const insightLower = summaryText.toLowerCase();
  
  // Check for obvious mismatches (basic keyword matching)
  const empathyKeywords = ['empathy', 'emotion', 'feeling', 'concern', 'worried', 'sad', 'happy', 'upset', 'recognizing emotions'];
  const hasEmpathyKeywords = empathyKeywords.some(kw => insightLower.includes(kw));
  const transcriptHasEmpathy = empathyKeywords.some(kw => transcriptLower.includes(kw));
  
  const dinosaurKeywords = ['dinosaur', 't-rex', 'rex', 'teeth', 'fossil', 'extinct', 'prehistoric'];
  const hasDinosaurKeywords = dinosaurKeywords.some(kw => insightLower.includes(kw));
  const transcriptHasDinosaur = dinosaurKeywords.some(kw => transcriptLower.includes(kw));
  
  // Detect potential mismatch (either backend detected it or frontend validation catches it)
  const potentialMismatch = backendDetectedMismatch || 
                           (hasEmpathyKeywords && transcriptHasDinosaur && !transcriptHasEmpathy) ||
                           (hasDinosaurKeywords && transcriptHasEmpathy && !transcriptHasDinosaur);

  return (
    <div className="recent-chat-summary">
      <div className="summary-main">
        <MessageSquare size={18} className="summary-icon" />
        <span className="summary-text">{summaryText}</span>
      </div>
      
      {potentialMismatch && (
        <div className="mismatch-warning">
          ⚠️ Note: This insight may not match the conversation below. Please verify.
        </div>
      )}
      
      {transcript && (
        <div className="transcript-section">
          <button 
            className="transcript-toggle"
            onClick={() => setShowTranscript(!showTranscript)}
            aria-label={showTranscript ? 'Hide transcript' : 'Show transcript'}
          >
            <FileText size={16} />
            <span>{showTranscript ? 'Hide' : 'Show'} Conversation Transcript</span>
            {showTranscript ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
          
          {showTranscript && (
            <div className="transcript-content">
              <div className="transcript-label">What {childName} said:</div>
              <div className="transcript-text">{transcript}</div>
              {potentialMismatch && (
                <div className="mismatch-note">
                  <strong>⚠️ Mismatch Detected:</strong> The insight above mentions topics that don't appear in this transcript. 
                  This may indicate the insight is from a different session or was incorrectly generated.
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

