#!/bin/bash

# Start the Curiosity Companion Dashboard

echo "🚀 Starting Curiosity Companion Dashboard..."
echo ""
echo "Make sure your backend server is running on http://localhost:3001"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please update VITE_API_BASE_URL if needed."
    else
        echo "VITE_API_BASE_URL=http://localhost:3001/api" > .env
        echo "✅ Created .env file with default settings."
    fi
    echo ""
fi

# Start the dev server
npm run dev

