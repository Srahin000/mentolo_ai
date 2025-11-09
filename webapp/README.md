# Curiosity Companion Dashboard

A beautiful, parent-friendly web dashboard for tracking child development through AI-powered conversations.

## Features

- 📊 **Daily Insights**: AI-generated insights from daily conversations
- 📈 **Development Snapshot**: Track language, cognitive, emotional, social, creativity, and physical development
- 🏆 **Strength Spotlight**: Celebrate your child's unique strengths and superpowers
- 📉 **Growth Timeline**: Visualize progress over time with interactive charts
- ✅ **Activities Checklist**: Personalized activities based on your child's interests
- 🎯 **Milestone Tracker**: Track developmental milestones and progress

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend server running on `http://localhost:3001` (or update `.env`)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Configure API endpoint:
   - Copy `.env.example` to `.env`
   - Update `VITE_API_BASE_URL` with your backend URL

3. Start development server:
```bash
npm run dev
```

4. Open your browser to `http://localhost:5173`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Configuration

Update `.env` file with your backend API URL:

```env
VITE_API_BASE_URL=http://localhost:3001/api
```

## Usage

1. Enter a child ID in the header (default: `test_user_places`)
2. Click "Refresh" to load dashboard data
3. Explore insights, strengths, activities, and milestones

## Tech Stack

- **React 19** - UI framework
- **Vite** - Build tool
- **Recharts** - Data visualization
- **Lucide React** - Icons
- **Axios** - HTTP client

## API Endpoints Used

- `GET /api/child-profile/:child_id` - Get child profile and development data
- `GET /api/dashboard?user_id=:id` - Get dashboard summary
- `GET /api/analytics/insights?user_id=:id` - Get AI insights
- `GET /api/recommendations/coaching-centers?user_id=:id` - Get location-based recommendations

## Design

The dashboard uses a warm, friendly color scheme:
- **Primary**: Soft blues and greens (trust, growth)
- **Accents**: Gold (achievements), Coral (activities)
- **Avoids**: Clinical whites and anxiety-inducing reds

## License

Part of the Curiosity Companion project.
