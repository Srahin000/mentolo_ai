# Picovoice Wake Word Setup

## Overview
HoloMentor uses Picovoice with a custom trained "Harry Potter" wake word model for hands-free activation.

## Files
- **Wake Word Model**: `Harry-Potter_en_wasm_v3_0_0/Harry-Potter_en_wasm_v3_0_0.ppn`
- **Service**: `mobile/PicovoiceWakeWord.js`
- **Integration**: `mobile/ARPlaceholder.js`

## Setup Steps

### 1. Get Picovoice Access Key
1. Go to https://console.picovoice.ai/
2. Sign up or log in
3. Copy your Access Key

### 2. Configure Mobile App

#### Option A: Environment Variable (Recommended)
Create a `.env` file in the `mobile/` directory:
```bash
PICOVOICE_ACCESS_KEY=your-access-key-here
```

#### Option B: Direct Configuration
Edit `mobile/config.js`:
```javascript
const PICOVOICE_ACCESS_KEY = 'your-access-key-here';
```

### 3. Install Dependencies
```bash
cd mobile
npm install @picovoice/picovoice-react-native @picovoice/react-native-voice-processor
```

### 4. Bundle Wake Word Model

For Expo managed workflow, you need to bundle the `.ppn` file:

1. Copy the wake word model to `mobile/assets/`:
```bash
mkdir -p mobile/assets
cp Harry-Potter_en_wasm_v3_0_0/Harry-Potter_en_wasm_v3_0_0.ppn mobile/assets/
```

2. Update `mobile/PicovoiceWakeWord.js`:
```javascript
const wakeWordModelPath = require('./assets/Harry-Potter_en_wasm_v3_0_0.ppn');
```

### 5. For Bare React Native Workflow

If using bare React Native (not Expo managed):

1. Add to `android/app/src/main/assets/`:
```bash
cp Harry-Potter_en_wasm_v3_0_0/Harry-Potter_en_wasm_v3_0_0.ppn android/app/src/main/assets/
```

2. Add to iOS bundle:
```bash
# Add to Xcode project and ensure it's included in bundle
```

3. Update path in `PicovoiceWakeWord.js`:
```javascript
// Android
const wakeWordModelPath = Platform.OS === 'android' 
  ? 'Harry-Potter_en_wasm_v3_0_0.ppn'
  : 'Harry-Potter_en_wasm_v3_0_0.ppn';
```

## Usage

The wake word detection starts automatically when the app loads. Users can say **"Harry Potter"** to activate the assistant.

### Features
- ✅ Hands-free activation
- ✅ Custom trained wake word
- ✅ Low power consumption
- ✅ Works offline (on-device processing)

### Testing

1. Start the app
2. Look for the green indicator: "🎤 Listening... Say 'Harry Potter'"
3. Say "Harry Potter" clearly
4. The assistant should activate automatically

## Troubleshooting

### "Picovoice not initialized"
- Check that `PICOVOICE_ACCESS_KEY` is set correctly
- Verify the access key is valid at https://console.picovoice.ai/

### "Wake word model not found"
- Ensure the `.ppn` file is in the correct location
- For Expo: Use `require()` to bundle the file
- For bare RN: Ensure file is in assets/bundle

### "Permission denied"
- Grant microphone permissions when prompted
- Check device settings if permissions were denied

### Wake word not detecting
- Speak clearly: "Harry Potter"
- Reduce background noise
- Check microphone is working
- Verify Picovoice service is initialized (check logs)

## Customization

To change the wake word or use a different model:

1. Train a new model at https://console.picovoice.ai/
2. Download the `.ppn` file
3. Replace the file in `Harry-Potter_en_wasm_v3_0_0/`
4. Update the path in `PicovoiceWakeWord.js`

## Notes

- Wake word detection runs on-device (privacy-friendly)
- No internet required for wake word detection
- After wake word is detected, the app connects to backend for AI processing
- The custom "Harry Potter" model is optimized for the wake phrase

