/**
 * Picovoice Wake Word Detection Service
 * Uses custom trained "Harry Potter" wake word model
 */

import { Picovoice } from '@picovoice/picovoice-react-native';
import { VoiceProcessor } from '@picovoice/react-native-voice-processor';

class PicovoiceWakeWordService {
  constructor() {
    this.picovoice = null;
    this.isListening = false;
    this.onWakeWordDetected = null;
    this.accessKey = null; // Picovoice Access Key from environment
  }

  /**
   * Initialize Picovoice with custom wake word model
   * @param {string} accessKey - Picovoice Access Key
   * @param {function} onWakeWordDetected - Callback when wake word is detected
   */
  async initialize(accessKey, onWakeWordDetected) {
    try {
      this.accessKey = accessKey;
      this.onWakeWordDetected = onWakeWordDetected;

      // Path to custom wake word model (.ppn file)
      // For Expo managed workflow, copy the .ppn file to mobile/assets/ and use:
      // const wakeWordModelPath = require('./assets/Harry-Potter_en_wasm_v3_0_0.ppn');
      
      // For development/testing, use the file from project root
      // Note: In production, bundle this file with your app
      const wakeWordModelPath = '../Harry-Potter_en_wasm_v3_0_0/Harry-Potter_en_wasm_v3_0_0.ppn';

      // Initialize Picovoice
      this.picovoice = await Picovoice.create(
        accessKey,
        wakeWordModelPath,
        this.onWakeWordCallback.bind(this),
        this.onErrorCallback.bind(this)
      );

      console.log('✅ Picovoice initialized with Harry Potter wake word');
      return true;
    } catch (error) {
      console.error('❌ Picovoice initialization error:', error);
      throw error;
    }
  }

  /**
   * Callback when wake word is detected
   */
  onWakeWordCallback() {
    console.log('🎤 Wake word "Harry Potter" detected!');
    if (this.onWakeWordDetected) {
      this.onWakeWordDetected();
    }
  }

  /**
   * Error callback
   */
  onErrorCallback(error) {
    console.error('Picovoice error:', error);
  }

  /**
   * Start listening for wake word
   */
  async start() {
    if (!this.picovoice) {
      throw new Error('Picovoice not initialized. Call initialize() first.');
    }

    if (this.isListening) {
      console.log('Already listening for wake word');
      return;
    }

    try {
      // Get audio frames from Picovoice
      const frameLength = this.picovoice.frameLength;
      const sampleRate = this.picovoice.sampleRate;

      // Start voice processor
      await VoiceProcessor.start(
        frameLength,
        sampleRate,
        true, // enableOverflow
        async (frames) => {
          // Process audio frames with Picovoice
          if (this.picovoice) {
            await this.picovoice.process(frames);
          }
        }
      );

      this.isListening = true;
      console.log('🎤 Listening for wake word "Harry Potter"...');
    } catch (error) {
      console.error('Error starting wake word detection:', error);
      throw error;
    }
  }

  /**
   * Stop listening for wake word
   */
  async stop() {
    if (!this.isListening) {
      return;
    }

    try {
      await VoiceProcessor.stop();
      this.isListening = false;
      console.log('🛑 Stopped listening for wake word');
    } catch (error) {
      console.error('Error stopping wake word detection:', error);
      throw error;
    }
  }

  /**
   * Release Picovoice resources
   */
  async release() {
    try {
      if (this.isListening) {
        await this.stop();
      }
      if (this.picovoice) {
        this.picovoice.delete();
        this.picovoice = null;
      }
      console.log('✅ Picovoice released');
    } catch (error) {
      console.error('Error releasing Picovoice:', error);
    }
  }

  /**
   * Check if Picovoice is available and initialized
   */
  isAvailable() {
    return this.picovoice !== null;
  }
}

export default new PicovoiceWakeWordService();

