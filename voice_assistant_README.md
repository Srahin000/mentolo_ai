# Voice Assistant with Wake Word Detection

A Python script that listens for a wake word, processes speech input, generates responses, and saves audio output.

## Features

- 🎤 **Wake Word Detection**: Listens for a customizable wake word
- 🗣️ **Speech-to-Text**: Converts speech to text using Google Speech Recognition
- 🤖 **Response Generation**: Uses your backend API or OpenAI to generate responses
- 🔊 **Text-to-Speech**: Converts responses to audio using ElevenLabs, gTTS, or pyttsx3
- 💾 **Audio Saving**: Saves all responses to audio files
- ⏱️ **Follow-up Input**: Waits 4 seconds after response for additional input
- 🔄 **Continuous Loop**: Returns to wake word listening after each interaction

## Installation

1. Install system dependencies (if needed):

```bash
# macOS
brew install portaudio

# Ubuntu/Debian
sudo apt-get install portaudio19-dev python3-pyaudio

# Windows (usually works with pip)
```

2. Install Python dependencies:

```bash
pip install -r requirements_voice_assistant.txt
```

## Configuration

Edit `voice_assistant.py` to customize:

- **Wake Word**: Change `WAKE_WORD = "hey assistant"` to your preferred phrase
- **Backend URL**: Set `API_BASE_URL` environment variable or edit the code
- **TTS Method**: The script tries ElevenLabs → gTTS → pyttsx3 in order

## Environment Variables (Optional)

```bash
# For backend API integration
export API_BASE_URL=http://localhost:3001/api

# For OpenAI fallback
export OPENAI_API_KEY=your_key_here
```

## Usage

Run the script:

```bash
python voice_assistant.py
```

### How It Works

1. **Listen for Wake Word**: Continuously listens for "hey assistant" (or your custom wake word)
2. **Capture Input**: After wake word detected, listens for your question/command
3. **Generate Response**: Sends input to backend API or OpenAI
4. **Save Audio**: Converts response to speech and saves to `storage/audio/responses/`
5. **Play Audio**: Plays the response audio
6. **Wait for More**: Waits 4 seconds for additional input
7. **Loop Back**: Returns to step 1

### Example Flow

```
🎤 Listening for wake word: 'hey assistant'...
Heard: hey assistant
✅ Wake word 'hey assistant' detected!
🎤 Listening for your input...
📝 You said: what's the weather today?
🤖 Generating response...
💬 Response: The weather today is sunny with a high of 75°F.
🔊 Converting to speech...
✅ Audio saved to: storage/audio/responses/response_20241109_143022.mp3
✅ Audio playback complete
⏳ Waiting 4 seconds for more input...
📝 Additional input: what about tomorrow?
💬 Response: Tomorrow will be partly cloudy with a high of 72°F.
...
🔄 Returning to wake word listening...
```

## Audio Output

All responses are saved to:
```
storage/audio/responses/response_YYYYMMDD_HHMMSS.mp3
```

## Troubleshooting

### "pyaudio not found"
- Install system dependencies first (portaudio)
- Then install pyaudio: `pip install pyaudio`

### "No speech detected"
- Check microphone permissions
- Adjust microphone volume
- Try speaking louder or closer to microphone

### "Backend API not available"
- Make sure your backend is running
- Check `API_BASE_URL` environment variable
- The script will fallback to OpenAI or simple responses

### "No TTS method available"
- Install at least one: `pip install gtts` or `pip install pyttsx3`
- gTTS requires internet, pyttsx3 works offline

## Customization

### Change Wake Word
```python
WAKE_WORD = "your custom wake word"
```

### Change Wait Time
```python
self.wait_for_more_input(wait_seconds=6)  # Change from 4 to 6 seconds
```

### Use Different TTS
Modify `text_to_speech()` method to prioritize your preferred TTS service.

## Integration with Existing Backend

The script automatically tries to use your existing backend:
- `/api/chat` for generating responses
- `/api/tts` for text-to-speech

Make sure your backend is running and accessible!

