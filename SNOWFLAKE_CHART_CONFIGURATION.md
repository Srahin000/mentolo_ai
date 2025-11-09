# Snowflake Dashboard Chart Configuration Guide

## Why All Graphs Look the Same

Snowflake dashboards default to **Line Charts** for most queries unless you explicitly configure the chart type. Each tile needs to be manually configured with the appropriate visualization type.

## How to Configure Chart Types in Snowflake

### Step-by-Step Instructions:

1. **Open Your Dashboard** in Snowflake
2. **Click on a Tile** to edit it
3. **Click "Visualization"** or the chart icon
4. **Select the appropriate chart type** from the dropdown:
   - Line Chart
   - Bar Chart
   - Area Chart
   - Pie Chart
   - Scorecard
   - Table
   - etc.

5. **Configure Axes**:
   - Set X-axis (usually date or category)
   - Set Y-axis (usually numeric values)
   - For multi-series charts, select which columns to display

6. **Save** the tile configuration

## Recommended Chart Types by Tile

| Tile | Query | Recommended Chart Type | Notes |
|------|-------|----------------------|-------|
| TILE 1 | Development Scores Over Time | **Line Chart (Multi-line)** | Shows 5 lines for different scores |
| TILE 2 | Vocabulary Growth | **Line Chart (Multi-line)** | Two lines: vocabulary_size, sentence_complexity |
| TILE 3 | Current Development Scores | **Bar Chart** | Horizontal or vertical bars |
| TILE 4 | Session Activity Metrics | **Scorecard** | 3 separate number displays |
| TILE 5 | Question Frequency & Curiosity | **Line Chart (Multi-line)** | Two lines showing trends |
| TILE 6 | Recent Sessions | **Table** | Already configured as table |
| TILE 7 | Overall Development Progress | **Area Chart** | Single area showing overall trend |
| TILE 8 | Strengths Distribution | **Pie Chart** | Shows distribution of strengths |
| TILE 9 | Engagement Metrics | **Line Chart** or **Bar Chart** | Multiple engagement metrics |
| TILE 10 | Grammar Accuracy Trend | **Line Chart (Multi-line)** | Grammar and complexity trends |
| TILE 11 | Emotional Intelligence | **Area Chart (Stacked)** | Shows emotional metrics over time |
| TILE 12 | Cognitive Patterns | **Bar Chart (Grouped)** | Grouped bars for cognitive metrics |
| TILE 13 | Top Strengths | **Pie Chart** | Distribution of top strengths |
| TILE 14 | Growth Areas | **Bar Chart (Horizontal)** | Horizontal bars work best for categories |
| TILE 15 | Session Quality | **Scorecard** | 4 separate metric displays |
| TILE 16 | Comprehensive Overview | **Table** | Already configured as table |

## Quick Fix: Configure All Tiles

1. Go through each tile one by one
2. Click the tile → Edit → Visualization
3. Select the chart type from the list above
4. Configure X and Y axes appropriately
5. Save

## Alternative: Use Different Query Structures

If you want charts to automatically detect the right type, you can restructure queries:

### For Bar Charts (Category + Value):
```sql
SELECT 
    'Language' as category,
    language_score as value
FROM child_development_trends
WHERE child_id = 'demo_child_tommy'
ORDER BY date DESC
LIMIT 1
UNION ALL
SELECT 'Cognitive', cognitive_score
-- etc.
```

### For Pie Charts (Category + Count):
```sql
SELECT 
    top_strength as category,
    COUNT(*) as value
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
GROUP BY top_strength
```

### For Scorecards (Single Value):
```sql
SELECT 
    COUNT(*) as total_sessions
FROM child_development_sessions
WHERE child_id = 'demo_child_tommy'
```

## Pro Tips

1. **Use consistent column names**: `date`, `category`, `value` help Snowflake auto-detect chart types
2. **Limit data points**: Too many points can make charts cluttered
3. **Use appropriate date ranges**: Filter to last 30/90 days for better visualization
4. **Group by date**: Aggregate daily data for cleaner line/area charts

## Troubleshooting

**Problem**: All charts show as line charts
**Solution**: Manually configure each tile's visualization type

**Problem**: Charts are empty
**Solution**: Check that `child_id = 'demo_child_tommy'` matches your data

**Problem**: Wrong data displayed
**Solution**: Verify the WHERE clause and date filters

**Problem**: Chart looks cluttered
**Solution**: Limit the number of series or use date filters

