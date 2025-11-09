# Avatar Web - HeyGen Realtime Avatar

Simple web app for interacting with HeyGen realtime avatars. Kid-friendly interface.

## Setup

1. **Install dependencies:**
   ```bash
   cd avatar-web
   npm install
   ```

2. **Configure API endpoint:**
   - Create `.env` file (optional):
   ```bash
   VITE_API_BASE_URL=http://localhost:3001/api
   ```
   - Or it will default to `http://localhost:3001/api`
   - If backend is on a different machine, use: `http://192.168.1.182:3001/api`

3. **Start the app:**
   ```bash
   npm run dev
   ```
   - App will run on `http://localhost:5174`

## Features

- Kid-friendly UI with large buttons and emojis
- Real-time avatar interaction via WebSocket
- Audio recording and playback
- Visual feedback (listening indicators, sound waves)
- Error handling with friendly messages

## Requirements

- Backend running on port 5000 with HeyGen service configured
- `HEYGEN_API_KEY` set in backend `.env` file
- Modern browser with WebSocket and Web Audio API support

## Notes

- This is a separate app from the main dashboard
- Runs on a different port (5174) so it can run alongside the dashboard
- If HeyGen doesn't work out, simply delete this `avatar-web/` directory

