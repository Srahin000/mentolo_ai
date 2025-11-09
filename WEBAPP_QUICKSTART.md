# 🎉 Curiosity Companion Dashboard - Quick Start

Your beautiful web dashboard is ready! Here's how to use it:

## 🚀 Starting the Dashboard

### Option 1: Using the start script
```bash
cd webapp
./start.sh
```

### Option 2: Manual start
```bash
cd webapp
npm run dev
```

The dashboard will open at **http://localhost:5173**

## 📋 Prerequisites

1. **Backend server must be running** on `http://localhost:3001`
   ```bash
   cd backend
   python app.py
   ```

2. **Test user profile** should exist (default: `test_user_places`)
   - You can create one using: `python setup_test_user.py`

## 🎨 Dashboard Features

### ✅ What's Built:

1. **Daily Insight Card** - AI-generated insights from conversations
2. **Development Snapshot Grid** - 6 development areas with scores
3. **Strength Spotlight** - Your child's superpowers and achievements
4. **Growth Timeline Chart** - Visual progress tracking (30 days)
5. **Activities Checklist** - Personalized weekly activities
6. **Milestone Tracker** - Developmental milestones progress

### 🎨 Design Features:

- **Warm, friendly color scheme** (soft blues/greens, gold, coral)
- **Mobile-responsive** design
- **Interactive charts** using Recharts
- **Beautiful icons** from Lucide React
- **Smooth animations** and transitions

## 🔧 Configuration

The API endpoint is configured in `webapp/.env`:
```env
VITE_API_BASE_URL=http://localhost:3001/api
```

If your backend runs on a different port or URL, update this file.

## 📊 Using the Dashboard

1. **Enter Child ID**: Type a child ID in the header (default: `test_user_places`)
2. **Click Refresh**: Load the latest data
3. **Explore**: View insights, strengths, activities, and milestones

## 🧪 Testing

To test with sample data:
```bash
# Create a test user with location and interests
python setup_test_user.py

# The dashboard will use: test_user_places
```

## 🐛 Troubleshooting

**Dashboard shows "Error Loading Dashboard":**
- Check that backend is running on port 3001
- Verify the child ID exists in your database
- Check browser console for API errors

**Charts not showing:**
- Make sure you have session data (run some conversations first)
- Check that trends data is available in the child profile

**API connection issues:**
- Verify `VITE_API_BASE_URL` in `.env` matches your backend URL
- Check CORS settings in backend if accessing from different origin

## 📦 Build for Production

```bash
cd webapp
npm run build
```

Output will be in `webapp/dist/` - ready to deploy!

## 🎯 Next Steps

- Add more child profiles
- Customize colors/themes
- Add export functionality (PDF reports)
- Integrate with mobile app
- Add real-time updates

---

**Enjoy your beautiful dashboard!** 🎊

