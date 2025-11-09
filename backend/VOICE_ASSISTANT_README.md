# Voice Assistant

A Python script that uses your backend services (Gemini + ElevenLabs) for a complete voice assistant experience.

## Features

- 🎤 **Wake Word Detection**: Listens for "hey assistant" (customizable)
- 🗣️ **Speech-to-Text**: Uses Google Speech Recognition
- 🤖 **Response Generation**: Uses your GeminiService directly
- 🔊 **Text-to-Speech**: Uses your ElevenLabsService directly
- 💾 **Audio Saving**: Saves all responses to `storage/audio/responses/`
- ⏱️ **Follow-up Input**: Waits 4 seconds after response for additional input
- 🔄 **Continuous Loop**: Returns to wake word listening after each interaction

## Quick Start

1. **Install dependencies** (if not already installed):
```bash
cd backend
pip install SpeechRecognition pygame gtts
```

2. **Set environment variables** (in `.env` file):
```bash
GEMINI_API_KEY=your_gemini_key
ELEVENLABS_API_KEY=your_elevenlabs_key
```

3. **Run the voice assistant**:
```bash
cd backend
python voice_assistant.py
```

## How It Works

The script directly imports and uses your backend services:

```python
from services.gemini_service import GeminiService
from services.elevenlabs_service import ElevenLabsService
```

### Flow

1. **Listen for Wake Word** → Continuously listens for "hey assistant"
2. **Capture Input** → After wake word, listens for your question
3. **Generate Response** → Uses `GeminiService.get_response()`
4. **Convert to Speech** → Uses `ElevenLabsService.text_to_speech()`
5. **Save Audio** → Saves to `storage/audio/responses/response_TIMESTAMP.mp3`
6. **Play Audio** → Plays the response
7. **Wait for More** → Waits 4 seconds for additional input
8. **Loop Back** → Returns to step 1

## Customization

### Change Wake Word
Edit `voice_assistant.py`:
```python
WAKE_WORD = "your custom wake word"
```

### Change Wait Time
Edit the `wait_for_more_input()` call:
```python
additional_input = self.wait_for_more_input(wait_seconds=6)  # Change from 4 to 6
```

### Change System Context
Edit the `SYSTEM_CONTEXT` variable to change how Gemini responds:
```python
SYSTEM_CONTEXT = """Your custom instructions here..."""
```

## Audio Output

All responses are saved to:
```
backend/storage/audio/responses/response_YYYYMMDD_HHMMSS.mp3
```

## Troubleshooting

### "Gemini service not available"
- Check that `GEMINI_API_KEY` is set in your `.env` file
- Verify the key is valid

### "ElevenLabs service not available"
- Check that `ELEVENLABS_API_KEY` is set
- The script will fallback to gTTS if ElevenLabs is unavailable

### "No speech detected"
- Check microphone permissions
- Adjust microphone volume
- Speak clearly and close to microphone

### "SpeechRecognition not installed"
```bash
pip install SpeechRecognition
```

### "pygame not installed" (for audio playback)
```bash
pip install pygame
```
Note: Audio will still be saved even without pygame, just won't play automatically.

## Example Session

```
🎤 Listening for wake word: 'hey assistant'...
Heard: hey assistant
✅ Wake word 'hey assistant' detected!
🎤 Listening for your input...
📝 You said: what's the weather today?
🤖 Generating response for: what's the weather today?
💬 Response: I don't have access to real-time weather data, but I'd be happy to help you find weather information!
🔊 Converting to speech...
✅ Audio saved to: storage/audio/responses/response_20241109_143022.mp3
✅ Audio playback complete
⏳ Waiting 4 seconds for more input...
📝 Additional input: tell me a joke
💬 Response: Why don't scientists trust atoms? Because they make up everything!
...
🔄 Returning to wake word listening...
```

## Integration with Backend

The voice assistant uses your existing services:
- ✅ **GeminiService**: For generating responses
- ✅ **ElevenLabsService**: For text-to-speech
- ✅ **Storage**: Saves audio to your existing storage structure

No HTTP requests needed - everything runs locally using your backend services directly!

