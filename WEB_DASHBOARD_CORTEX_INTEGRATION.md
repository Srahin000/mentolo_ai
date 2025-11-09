# Web Dashboard + Cortex AI Integration Guide

## Overview

Your React web dashboard now includes **Snowflake Cortex AI** features:
- ✅ **Cortex Insights Component** - AI-powered analysis (trends, patterns, benchmarks)
- ✅ **Cortex Chatbot** - Natural language queries using Cortex Analyst
- ✅ **Automatic Fallback** - Gracefully handles Cortex unavailability

---

## New Components Added

### 1. **CortexInsights Component**
**Location**: `webapp/src/components/CortexInsights.jsx`

**Features**:
- Three tabs: Trends, Patterns, Benchmarks
- Displays AI-generated insights from Cortex
- Shows development trajectory, strengths, growth areas
- Pattern detection and correlations
- Benchmark comparisons

**Usage**:
```jsx
<CortexInsights childId="demo_child_tommy" />
```

### 2. **CortexChatbot Component**
**Location**: `webapp/src/components/CortexChatbot.jsx`

**Features**:
- Interactive chatbot interface
- Natural language queries about child development
- Suggested questions for easy interaction
- Real-time responses from Cortex Analyst
- Graceful error handling

**Usage**:
```jsx
<CortexChatbot childId="demo_child_tommy" childName="Tommy" />
```

---

## API Integration

### New API Functions

**`getCortexAnalysis(childId, analysisType, days)`**
- Fetches Cortex AI analysis
- Types: `'trends'`, `'patterns'`, `'benchmarks'`
- Returns structured insights

**`queryCortexAnalyst(childId, question)`**
- Sends natural language question to Cortex Analyst
- Returns AI-generated answer
- Handles unavailability gracefully

---

## Dashboard Layout

The dashboard now includes Cortex components:

```
┌─────────────────────────────────────────────────┐
│  Daily Insight Card                              │
├─────────────────────────────────────────────────┤
│  Development Snapshot Grid                      │
├─────────────────────────────────────────────────┤
│  Strength Spotlight                              │
├─────────────────────────────────────────────────┤
│  Growth Timeline Chart                           │
├─────────────────────────────────────────────────┤
│  Insights Panel                                  │
├─────────────────────────────────────────────────┤
│  Engagement Metrics                              │
├─────────────────────────────────────────────────┤
│  Emotional Intelligence                          │
├─────────────────────────────────────────────────┤
│  Cognitive Patterns                              │
├─────────────────────────────────────────────────┤
│  Language Details                                │
├─────────────────────────────────────────────────┤
│  Speech Clarity                                  │
├─────────────────────────────────────────────────┤
│  🆕 Cortex AI Insights (NEW)                     │
│     - Trends Tab                                 │
│     - Patterns Tab                                │
│     - Benchmarks Tab                             │
├─────────────────────────────────────────────────┤
│  🆕 Cortex Chatbot (NEW)                         │
│     - Ask questions in natural language          │
│     - Get AI-powered answers                     │
├─────────────────────────────────────────────────┤
│  Places Recommendations                         │
├─────────────────────────────────────────────────┤
│  Activities Checklist                            │
├─────────────────────────────────────────────────┤
│  Milestone Tracker                               │
└─────────────────────────────────────────────────┘
```

---

## How It Works

### 1. Cortex Insights Flow

```
User opens dashboard
    ↓
CortexInsights component loads
    ↓
Calls /api/cortex/analyze
    ↓
Backend uses Cortex to analyze data
    ↓
Returns AI-generated insights
    ↓
Displayed in tabs (Trends/Patterns/Benchmarks)
```

### 2. Chatbot Flow

```
User types question
    ↓
Calls /api/cortex/query
    ↓
Backend uses Cortex Analyst
    ↓
Returns natural language answer
    ↓
Displayed in chat interface
```

---

## Features

### Cortex Insights Tabs

**Trends Tab**:
- Development trajectory (improving/stable/declining)
- Top strengths with evidence
- Growth areas with recommendations
- Actionable next steps

**Patterns Tab**:
- Correlations between development areas
- Temporal patterns (day of week, time patterns)
- Anomalies and outliers

**Benchmarks Tab**:
- Comparison to age-appropriate benchmarks
- Areas ahead of benchmark
- Areas on track
- Areas needing support

### Chatbot Features

**Suggested Questions**:
- "What are the main trends in language development?"
- "How has emotional intelligence changed over time?"
- "What activities would help improve cognitive scores?"
- "How does this child compare to typical 4-year-old development?"
- "What are the strongest areas of development?"
- "What should we focus on next?"

**Interactive**:
- Type custom questions
- Real-time responses
- Chat history
- Error handling

---

## Fallback Behavior

### If Cortex Unavailable

**Cortex Insights**:
- Shows error message
- Displays: "Using Gemini Pro fallback for analysis"
- Standard insights still available

**Chatbot**:
- Shows warning message
- Suggests using standard insights
- Prevents further queries

---

## Styling

Both components use:
- Professional theme colors
- Consistent with existing dashboard
- Responsive design
- Smooth animations
- Accessible UI

**CSS Files**:
- `CortexInsights.css`
- `CortexChatbot.css`

---

## Testing

### Test Cortex Insights

1. Open dashboard
2. Scroll to "Cortex AI Insights" section
3. Click through tabs (Trends, Patterns, Benchmarks)
4. Verify insights load correctly

### Test Chatbot

1. Scroll to "Cortex Chatbot" section
2. Click a suggested question
3. Or type a custom question
4. Verify response appears

### Test Fallback

If Cortex unavailable:
1. Components show error messages
2. Dashboard still functions
3. Standard insights available

---

## Hackathon Showcase

### For Judges

**Show**:
1. Standard dashboard (existing features)
2. **Cortex Insights** - "AI-powered analysis using Snowflake Cortex"
3. **Chatbot** - "Ask questions in natural language"
4. Explain: "All powered by Snowflake Cortex AI"

**Demo Flow**:
1. Show standard visualizations
2. Click to Cortex Insights → Show AI-generated trends
3. Switch to Patterns tab → Show correlations
4. Open Chatbot → Ask "What are the main trends?"
5. Show real-time AI response

---

## Benefits

### For Hackathon

✅ **Showcases Snowflake Cortex AI**
- Cortex Complete for insights
- Cortex Analyst for chatbot
- Native Snowflake integration

✅ **Interactive Demo**
- Judges can ask questions
- Real-time AI responses
- Professional UI

✅ **Complete Solution**
- Web dashboard + Snowflake native dashboard
- Both use same Cortex backend
- Consistent insights

---

## Next Steps

1. **Test the components**:
   ```bash
   cd webapp
   npm run dev
   ```

2. **Verify Cortex availability**:
   - Check backend logs for Cortex initialization
   - Test `/api/cortex/analyze` endpoint
   - Test `/api/cortex/query` endpoint

3. **Customize if needed**:
   - Adjust suggested questions
   - Modify styling
   - Add more tabs/features

---

## Summary

Your web dashboard now includes:
- ✅ Cortex AI Insights (3 tabs: Trends, Patterns, Benchmarks)
- ✅ Interactive Chatbot (natural language queries)
- ✅ Graceful fallback handling
- ✅ Professional UI matching existing dashboard
- ✅ Ready for hackathon showcase

**Both dashboards work together**:
- **Snowflake Native Dashboard**: For judges to see Snowflake features
- **Web Dashboard**: For interactive demo and better UX

Perfect for hackathon presentation! 🚀

