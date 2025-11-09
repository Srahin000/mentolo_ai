# 🎨 Dummy Profile Guide

## ✅ Dummy Profile Created!

A complete dummy child profile has been created in Snowflake with realistic development data.

### 📋 Profile Details

- **Child ID**: `demo_child_tommy`
- **Name**: Tommy
- **Age**: 5 years old
- **Location**: New York, NY
- **Interests**: Dinosaurs, space, building, storytelling

### 📊 Data Included

1. **15 Development Sessions** (spread over last 30 days)
   - Each session includes full analysis with:
     - Daily insights
     - Development snapshot (6 areas)
     - Strengths and achievements
     - Growth opportunities
     - Personalized activities
     - Milestone progress
     - Vocabulary analysis
     - Cognitive indicators
     - Emotional intelligence
     - Social skills
     - Creativity indicators

2. **30 Days of Trend Data**
   - Daily aggregated scores
   - Vocabulary growth progression
   - Sentence complexity trends
   - Question frequency
   - Curiosity scores
   - Strengths and growth areas

### 🚀 View in Dashboard

1. **Start the dashboard** (if not running):
   ```bash
   cd webapp
   npm run dev
   ```

2. **Open browser**: http://localhost:5173

3. **Enter Child ID**: `demo_child_tommy`

4. **Click "Refresh"** to load data

### 📈 What You'll See

- **Daily Insight**: AI-generated insights from conversations
- **Development Snapshot**: 6 development areas with scores (60-90 range)
- **Strength Spotlight**: 3 superpowers (Storytelling, Question Asking, Empathy)
- **Growth Timeline**: 30-day progress chart showing vocabulary and complexity growth
- **Activities Checklist**: 3 personalized activities
- **Milestone Tracker**: Progress on developmental milestones

### 🔄 Recreate the Profile

If you want to recreate or update the dummy profile:

```bash
python create_dummy_profile.py
```

This will:
- Clear existing sessions and trends for `demo_child_tommy`
- Create fresh data with progressive scores
- Show realistic development over time

### 🎯 Test Different Scenarios

You can modify `create_dummy_profile.py` to:
- Change the child's age
- Adjust the number of sessions
- Modify the progress trajectory
- Add different strengths or interests

### 📝 Notes

- The profile shows **progressive improvement** over time
- Scores increase from ~60 to ~90 over 30 days
- Vocabulary grows from 800 to 875 words
- Sentence complexity increases from 6.5 to 8.0
- All data is stored in Snowflake and accessible via API

### 🐛 Troubleshooting

**Dashboard shows "Error Loading Dashboard":**
- Make sure backend is running: `cd backend && python app.py`
- Verify Snowflake connection is working
- Check that child ID is exactly: `demo_child_tommy`

**No data showing:**
- Run the create script again: `python create_dummy_profile.py`
- Check Snowflake connection in backend logs
- Verify API endpoint: `curl http://localhost:3001/api/child-profile/demo_child_tommy`

---

**Enjoy exploring the dashboard with realistic data!** 🎉

