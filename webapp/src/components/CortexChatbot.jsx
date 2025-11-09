/**
 * Cortex Analyst Chatbot Component
 * Interactive chatbot using Snowflake Cortex Analyst for natural language queries
 */

import React, { useState } from 'react';
import { queryCortexAnalyst } from '../services/api';
import { MessageCircle, Send, Loader2, Bot, AlertCircle, Sparkles } from 'lucide-react';
import './CortexChatbot.css';

const SUGGESTED_QUESTIONS = [
  "What are the main trends in language development?",
  "How has emotional intelligence changed over time?",
  "What activities would help improve cognitive scores?",
  "How does this child compare to typical development for their age?",
  "What are the strongest areas of development?",
  "What should we focus on next?",
  "What are the biggest growth opportunities?",
  "How is vocabulary progressing?",
  "What social skills are emerging?",
  "Are there any concerns I should watch for?",
];

function CortexChatbot({ childId, childName = 'Your child' }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [cortexAvailable, setCortexAvailable] = useState(true);

  const handleSend = async (question = null) => {
    const questionText = question || input.trim();
    if (!questionText) return;

    // Add user message
    const userMessage = {
      role: 'user',
      content: questionText,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await queryCortexAnalyst(childId, questionText);
      
      if (response.available) {
        const botMessage = {
          role: 'assistant',
          content: response.answer,
          timestamp: new Date(),
          source: 'Cortex Analyst',
        };
        setMessages(prev => [...prev, botMessage]);
        setCortexAvailable(true);
      } else {
        const botMessage = {
          role: 'assistant',
          content: response.message || 'Cortex Analyst is not available in this region. Please use the standard insights instead.',
          timestamp: new Date(),
          source: 'System',
          error: true,
        };
        setMessages(prev => [...prev, botMessage]);
        setCortexAvailable(false);
      }
    } catch (error) {
      const botMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again or use the standard insights.',
        timestamp: new Date(),
        source: 'System',
        error: true,
      };
      setMessages(prev => [...prev, botMessage]);
      setCortexAvailable(false);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="cortex-chatbot">
      <div className="chatbot-header">
        <div className="chatbot-title">
          <Bot size={20} />
          <h3>Ask About {childName}'s Development</h3>
        </div>
        {cortexAvailable && (
          <div className="cortex-badge-small">
            <Sparkles size={12} />
            Cortex AI
          </div>
        )}
      </div>

      <div className="chatbot-messages">
        {messages.length === 0 && (
          <div className="chatbot-welcome">
            <Bot size={32} />
            <p>Ask me anything about {childName}'s development!</p>
            <div className="suggested-questions">
              <p>Try asking about {childName}'s development:</p>
              <div className="suggested-questions-grid">
                {SUGGESTED_QUESTIONS.slice(0, 6).map((q, idx) => (
                  <button
                    key={idx}
                    className="suggested-question"
                    onClick={() => handleSend(q)}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`chatbot-message ${msg.role}`}>
            <div className="message-content">
              {msg.role === 'user' ? (
                <>
                  <div className="message-bubble user">
                    {msg.content}
                  </div>
                </>
              ) : (
                <>
                  <Bot size={16} className="message-icon" />
                  <div className={`message-bubble assistant ${msg.error ? 'error' : ''}`}>
                    {msg.content}
                    {msg.source && (
                      <small className="message-source">{msg.source}</small>
                    )}
                  </div>
                </>
              )}
            </div>
            <small className="message-time">
              {msg.timestamp.toLocaleTimeString()}
            </small>
          </div>
        ))}

        {loading && (
          <div className="chatbot-message assistant">
            <Bot size={16} className="message-icon" />
            <div className="message-bubble assistant loading">
              <Loader2 className="spinner-small" />
              <span>Analyzing data...</span>
            </div>
          </div>
        )}
      </div>

      <div className="chatbot-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about development trends, strengths, recommendations..."
          disabled={loading}
        />
        <button
          onClick={() => handleSend()}
          disabled={loading || !input.trim()}
          className="send-button"
        >
          <Send size={18} />
        </button>
      </div>

      {!cortexAvailable && (
        <div className="chatbot-warning">
          <AlertCircle size={16} />
          <span>Cortex Analyst not available. Using standard insights.</span>
        </div>
      )}
    </div>
  );
}

export default CortexChatbot;

