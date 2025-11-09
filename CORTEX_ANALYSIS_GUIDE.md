# Snowflake Cortex Analysis Guide

## Overview

We've integrated **Snowflake Cortex** for advanced longitudinal analysis of child development data. 

**Important**: Cortex works on data that has already been analyzed by Gemini Pro. The workflow is:
1. **Individual sessions** → Gemini Pro analyzes → Stores in Snowflake
2. **Multiple sessions** → Cortex analyzes aggregated data → Long-term insights

Cortex provides AI-powered insights that go beyond standard SQL queries for long-term trend analysis.

## Features

### 1. **Longitudinal Trend Analysis** (`analyze_longitudinal_trends`)
- Analyzes 90 days of development data
- Generates insights about:
  - Overall development trajectory (improving/stable/declining)
  - Top strengths based on data patterns
  - Growth areas needing attention
  - Predictive insights about future development
  - Actionable recommendations for parents

### 2. **Pattern Detection** (`detect_patterns`)
- Identifies correlations between development areas
- Detects temporal patterns (e.g., higher scores on certain days)
- Finds anomalies or outliers
- Discovers predictive patterns

### 3. **Benchmark Comparison** (`compare_to_benchmarks`)
- Compares child's scores to age-appropriate benchmarks
- Identifies areas ahead of benchmarks
- Highlights areas needing support
- Provides specific recommendations

### 4. **Natural Language Queries** (`generate_insights_query`)
- Use Cortex Analyst to ask questions in plain English
- Example: "What are the main trends in language development?"
- Answers based on actual data in Snowflake

## Region Availability

⚠️ **Important**: Cortex features may not be available in all Snowflake regions (e.g., Australia/Azure).

**Our implementation includes automatic fallback:**
- If Cortex is unavailable → Uses Gemini Pro for analysis
- If Cortex Analyst is unavailable → Returns helpful error message
- Standard SQL queries always work (region-agnostic)

## API Endpoints

### 1. Automatic Integration

Cortex is automatically used in `/api/child-profile/<child_id>` when available:

```bash
GET /api/child-profile/demo_child_tommy
```

**Response includes:**
```json
{
  "trends": {
    "vocabulary_growth": [...],
    "complexity_progression": [...],
    "cortex_insights": {
      "trajectory": "improving",
      "strengths": [...],
      "growth_areas": [...],
      "predictions": [...],
      "recommendations": [...]
    },
    "analysis_source": "cortex"  // or "standard" if Cortex unavailable
  }
}
```

### 2. Direct Cortex Analysis

**POST `/api/cortex/analyze`**

Request:
```json
{
  "child_id": "demo_child_tommy",
  "analysis_type": "trends|patterns|benchmarks",
  "days": 90
}
```

Response:
```json
{
  "available": true,
  "source": "cortex",
  "analysis": {
    "trajectory": "improving",
    "strengths": [
      {
        "area": "Language Development",
        "evidence": "Vocabulary growth rate of 15 words/week",
        "why_matters": "Indicates strong language acquisition"
      }
    ],
    "growth_areas": [...],
    "predictions": [...],
    "recommendations": [...]
  }
}
```

### 3. Natural Language Queries

**POST `/api/cortex/query`**

Request:
```json
{
  "child_id": "demo_child_tommy",
  "question": "What are the main trends in language development over the past 3 months?"
}
```

Response:
```json
{
  "available": true,
  "source": "cortex_analyst",
  "answer": "Based on the data, language development shows...",
  "question": "What are the main trends in language development over the past 3 months?"
}
```

## Checking Cortex Availability

### Health Check

```bash
GET /api/health
```

Response includes:
```json
{
  "services": {
    "cortex": true  // or false if unavailable
  }
}
```

### Server Logs

When the server starts, you'll see:
- ✅ `Cortex Analysis Service initialized` - Cortex is available
- ℹ️ `Cortex not available in region, will use Gemini Pro fallback` - Cortex unavailable

## How It Works

### 1. Initialization

```python
# In app.py
cortex_service = CortexAnalysisService(snowflake_service.conn)
if cortex_service.is_available():
    logger.info("✅ Cortex Analysis Service initialized")
```

### 2. Automatic Fallback

If Cortex is unavailable, the system:
1. Detects unavailability during initialization
2. Logs a warning message
3. Uses Gemini Pro for analysis instead
4. Returns `analysis_source: "standard"` in responses

### 3. Data Flow

```
Child Development Data (Snowflake)
    ↓
Cortex Analysis Service
    ↓
[If Available] → Cortex LLM Functions → AI Insights
[If Unavailable] → Gemini Pro → AI Insights
    ↓
Dashboard / API Response
```

## Example Use Cases

### 1. Parent Dashboard

The dashboard automatically uses Cortex insights when available:

```javascript
// Frontend automatically receives cortex_insights
const response = await fetch('/api/child-profile/demo_child_tommy');
const data = await response.json();

if (data.trends.cortex_insights) {
  // Display Cortex-powered insights
  console.log(data.trends.cortex_insights.recommendations);
}
```

### 2. Custom Analysis

```python
import requests

# Analyze patterns
response = requests.post('http://localhost:5000/api/cortex/analyze', json={
    'child_id': 'demo_child_tommy',
    'analysis_type': 'patterns',
    'days': 90
})

patterns = response.json()
print(patterns['patterns']['correlations'])
```

### 3. Natural Language Questions

```python
# Ask questions about development
response = requests.post('http://localhost:5000/api/cortex/query', json={
    'child_id': 'demo_child_tommy',
    'question': 'How has emotional intelligence changed over time?'
})

answer = response.json()['answer']
print(answer)
```

## Benefits of Cortex

### vs. Standard SQL

| Feature | Standard SQL | Cortex |
|---------|-------------|--------|
| Trend Analysis | Basic aggregations | AI-powered insights |
| Pattern Detection | Manual queries | Automatic detection |
| Recommendations | None | AI-generated |
| Natural Language | Not supported | Supported (Analyst) |
| Predictive Insights | None | Included |

### vs. Gemini Pro Fallback

| Feature | Cortex | Gemini Pro |
|---------|--------|-----------|
| Runs in Snowflake | ✅ Yes | ❌ External API |
| Data Privacy | ✅ In Snowflake | ⚠️ External |
| Cost | ✅ Included in Snowflake | 💰 API costs |
| Region Availability | ⚠️ Limited | ✅ Global |
| Speed | ✅ Fast (in-database) | ⚠️ API latency |

## Troubleshooting

### "Cortex not available in region"

**Solution**: This is expected in some regions (e.g., Australia/Azure). The system automatically falls back to Gemini Pro.

### "Cortex Analyst not available"

**Solution**: Cortex Analyst has stricter region requirements. Use `/api/cortex/analyze` instead for analysis.

### "Permission denied"

**Solution**: Ensure your Snowflake user has:
- `USAGE` on `SNOWFLAKE.CORTEX` schema
- `EXECUTE` on Cortex functions

### Testing Cortex Availability

```python
from backend.services.cortex_analysis_service import CortexAnalysisService
from backend.services.snowflake_service import SnowflakeService

snowflake = SnowflakeService()
if snowflake.is_available():
    cortex = CortexAnalysisService(snowflake.conn)
    print(f"Cortex available: {cortex.is_available()}")
```

## Next Steps

1. **Test Cortex availability** in your region
2. **Use `/api/child-profile`** to see Cortex insights automatically
3. **Try `/api/cortex/analyze`** for custom analysis
4. **Explore `/api/cortex/query`** for natural language questions

## Summary

- ✅ Cortex provides advanced AI analysis for longitudinal data
- ✅ Automatic fallback to Gemini Pro if Cortex unavailable
- ✅ Works seamlessly with existing dashboard
- ✅ Region-aware (handles unavailability gracefully)
- ✅ No code changes needed - automatic integration

The system is designed to work optimally when Cortex is available, but gracefully degrades to Gemini Pro when it's not, ensuring your application works in all regions.

