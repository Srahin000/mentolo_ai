#!/bin/bash

# Voice Assistant Runner
# This script ensures all dependencies are available

echo "=========================================="
echo "Voice Assistant Setup & Runner"
echo "=========================================="
echo ""

# Detect which Python to use (prefer conda/current environment)
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "❌ No Python found!"
    exit 1
fi

echo "Using Python: $PYTHON_CMD"
$PYTHON_CMD --version
echo ""

# Check if we have the required packages
echo "Checking Python packages..."

$PYTHON_CMD -c "import pvporcupine" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ pvporcupine not installed"
    echo "Run: $PYTHON_CMD -m pip install pvporcupine pyaudio python-dotenv requests SpeechRecognition pygame"
    exit 1
fi

$PYTHON_CMD -c "import pyaudio" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ pyaudio not installed"
    echo "Run: $PYTHON_CMD -m pip install pyaudio"
    echo "On Mac, you might need: brew install portaudio && $PYTHON_CMD -m pip install pyaudio"
    exit 1
fi

echo "✅ All packages installed"
echo ""

# Check for wake word model
if [ ! -f "Harry-Potter_en_mac_v3_0_0/Harry-Potter_en_mac_v3_0_0.ppn" ]; then
    echo "❌ Wake word model not found!"
    echo "Expected: Harry-Potter_en_mac_v3_0_0/Harry-Potter_en_mac_v3_0_0.ppn"
    exit 1
fi

echo "✅ Wake word model found"
echo ""

# Check for access key
if [ -z "$PICOVOICE_ACCESS_KEY" ]; then
    echo "⚠️  PICOVOICE_ACCESS_KEY not set in environment"
    echo "Loading from .env file..."
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | grep PICOVOICE_ACCESS_KEY | xargs)
    fi
fi

if [ -z "$PICOVOICE_ACCESS_KEY" ]; then
    echo "❌ PICOVOICE_ACCESS_KEY still not set!"
    echo "Add it to your .env file or export it"
    exit 1
fi

echo "✅ Picovoice access key found"
echo ""

# Run the assistant
echo "🚀 Starting Voice Assistant..."
echo "Say 'Harry Potter' to activate"
echo "Press Ctrl+C to stop"
echo ""

$PYTHON_CMD voice_assistant.py

