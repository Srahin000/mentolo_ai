/**
 * HoloMentor Mobile - AR Placeholder Screen
 * Displays camera view with floating "Ask" button and speech bubble overlay
 * This will later be replaced with Unity AR scene
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Dimensions,
} from 'react-native';
import { Camera } from 'expo-camera';
import { Audio } from 'expo-av';
import { askQuestion } from './api';
import { StatusBar } from 'expo-status-bar';
import picovoiceService from './PicovoiceWakeWord';
import { getConfig } from './config';

const { width, height } = Dimensions.get('window');

export default function ARPlaceholder() {
  const [hasPermission, setHasPermission] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [responseText, setResponseText] = useState('');
  const [emotion, setEmotion] = useState('');
  const [showSpeechBubble, setShowSpeechBubble] = useState(false);
  const [sound, setSound] = useState(null);
  const [wakeWordActive, setWakeWordActive] = useState(false);
  const [isListeningForWakeWord, setIsListeningForWakeWord] = useState(false);
  const [wakeWordDetected, setWakeWordDetected] = useState(false);
  const [detectionCount, setDetectionCount] = useState(0);
  const cameraRef = useRef(null);

  useEffect(() => {
    // Request camera permission
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    })();

    // Initialize Picovoice wake word detection
    (async () => {
      try {
        const config = getConfig();
        const picovoiceAccessKey = config.PICOVOICE_ACCESS_KEY;
        
        if (picovoiceAccessKey) {
          await picovoiceService.initialize(
            picovoiceAccessKey,
            handleWakeWordDetected
          );
          await picovoiceService.start();
          setIsListeningForWakeWord(true);
          console.log('✅ Wake word detection active - say "Harry Potter"');
        } else {
          console.warn('⚠️  Picovoice Access Key not found. Wake word detection disabled.');
        }
      } catch (error) {
        console.error('Failed to initialize Picovoice:', error);
        // Continue without wake word detection
      }
    })();

    // Cleanup on unmount
    return () => {
      if (sound) {
        sound.unloadAsync();
      }
      picovoiceService.release();
    };
  }, []);

  const handleWakeWordDetected = () => {
    const count = detectionCount + 1;
    setDetectionCount(count);
    setWakeWordDetected(true);
    setWakeWordActive(true);
    
    // Print to console
    console.log('═══════════════════════════════════════════════════════');
    console.log('🎤🎤🎤 WAKE WORD DETECTED! 🎤🎤🎤');
    console.log('   "Harry Potter" detected!');
    console.log(`   Detection count: ${count}`);
    console.log('   Activating assistant...');
    console.log('═══════════════════════════════════════════════════════');
    
    // Show detection for 2 seconds, then activate
    setTimeout(() => {
      setWakeWordDetected(false);
      // Automatically trigger question when wake word is detected
      handleAskQuestion();
    }, 2000);
  };

  const handleAskQuestion = async () => {
    // For now, use a test question
    // Later: integrate speech-to-text or text input
    const testQuestion = "What is photosynthesis? Keep it brief.";

    setIsLoading(true);
    setShowSpeechBubble(false);
    setResponseText('');

    try {
      // Call the API
      const response = await askQuestion(testQuestion);

      // Update UI
      setResponseText(response.text);
      setEmotion(response.emotion);
      setShowSpeechBubble(true);

      // Play audio response
      await playAudioResponse(response.audio_url);

    } catch (error) {
      console.error('Error asking question:', error);
      Alert.alert(
        'Error',
        error.message || 'Failed to get response from AI. Check your backend connection.',
        [{ text: 'OK' }]
      );
    } finally {
      setIsLoading(false);
    }
  };

  const playAudioResponse = async (audioUrl) => {
    try {
      // Stop any currently playing sound
      if (sound) {
        await sound.unloadAsync();
      }

      // Create and play new sound
      const { sound: newSound } = await Audio.Sound.createAsync(
        { uri: audioUrl },
        { shouldPlay: true }
      );

      setSound(newSound);

      // Wait for playback to finish
      await new Promise((resolve) => {
        newSound.setOnPlaybackStatusUpdate((status) => {
          if (status.didJustFinish) {
            resolve();
          }
        });
      });

    } catch (error) {
      console.error('Error playing audio:', error);
      Alert.alert('Audio Error', 'Failed to play audio response.');
    }
  };

  if (hasPermission === null) {
    return (
      <View style={styles.container}>
        <Text>Requesting camera permission...</Text>
      </View>
    );
  }

  if (hasPermission === false) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Camera permission is required for AR features.</Text>
        <TouchableOpacity
          style={styles.button}
          onPress={async () => {
            const { status } = await Camera.requestCameraPermissionsAsync();
            setHasPermission(status === 'granted');
          }}
        >
          <Text style={styles.buttonText}>Grant Permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      {/* Camera View */}
      <Camera
        ref={cameraRef}
        style={styles.camera}
        type={Camera.Constants.Type.back}
      />

      {/* Speech Bubble Overlay */}
      {showSpeechBubble && responseText && (
        <View style={styles.speechBubble}>
          <View style={styles.speechBubbleContent}>
            {emotion && (
              <Text style={styles.emotionBadge}>Emotion: {emotion}</Text>
            )}
            <Text style={styles.speechText}>{responseText}</Text>
            <TouchableOpacity
              style={styles.closeButton}
              onPress={() => setShowSpeechBubble(false)}
            >
              <Text style={styles.closeButtonText}>✕</Text>
            </TouchableOpacity>
          </View>
          <View style={styles.speechBubbleTail} />
        </View>
      )}

      {/* Floating Ask Button */}
      <TouchableOpacity
        style={[styles.askButton, isLoading && styles.askButtonDisabled]}
        onPress={handleAskQuestion}
        disabled={isLoading}
      >
        {isLoading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.askButtonText}>Ask</Text>
        )}
      </TouchableOpacity>

      {/* Wake Word Status Indicator */}
      {isListeningForWakeWord && !wakeWordDetected && (
        <View style={styles.wakeWordIndicator}>
          <Text style={styles.wakeWordText}>
            🎤 Listening... Say "Harry Potter"
          </Text>
        </View>
      )}

      {/* Wake Word Detected Indicator */}
      {wakeWordDetected && (
        <View style={styles.wakeWordDetectedIndicator}>
          <Text style={styles.wakeWordDetectedText}>
            🎤🎤🎤 DETECTED! 🎤🎤🎤
          </Text>
          <Text style={styles.wakeWordDetectedSubtext}>
            "Harry Potter" detected! ({detectionCount})
          </Text>
        </View>
      )}

      {/* Loading Indicator */}
      {isLoading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#fff" />
          <Text style={styles.loadingText}>Thinking...</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  camera: {
    flex: 1,
  },
  askButton: {
    position: 'absolute',
    bottom: 50,
    alignSelf: 'center',
    backgroundColor: '#4CAF50',
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  askButtonDisabled: {
    backgroundColor: '#666',
  },
  askButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  speechBubble: {
    position: 'absolute',
    top: 100,
    left: 20,
    right: 20,
    maxWidth: width - 40,
  },
  speechBubbleContent: {
    backgroundColor: '#fff',
    borderRadius: 20,
    padding: 16,
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  emotionBadge: {
    fontSize: 12,
    color: '#666',
    marginBottom: 8,
    fontStyle: 'italic',
  },
  speechText: {
    fontSize: 16,
    color: '#333',
    lineHeight: 24,
  },
  closeButton: {
    position: 'absolute',
    top: 8,
    right: 8,
    width: 24,
    height: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeButtonText: {
    fontSize: 18,
    color: '#999',
  },
  speechBubbleTail: {
    position: 'absolute',
    bottom: -10,
    left: 30,
    width: 0,
    height: 0,
    borderLeftWidth: 10,
    borderRightWidth: 10,
    borderTopWidth: 10,
    borderLeftColor: 'transparent',
    borderRightColor: 'transparent',
    borderTopColor: '#fff',
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#fff',
    marginTop: 16,
    fontSize: 16,
  },
  errorText: {
    color: '#fff',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
  },
  button: {
    backgroundColor: '#4CAF50',
    padding: 12,
    borderRadius: 8,
    alignSelf: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  wakeWordIndicator: {
    position: 'absolute',
    top: 50,
    alignSelf: 'center',
    backgroundColor: 'rgba(76, 175, 80, 0.9)',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  wakeWordText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  wakeWordDetectedIndicator: {
    position: 'absolute',
    top: 50,
    alignSelf: 'center',
    backgroundColor: '#4CAF50',
    paddingHorizontal: 30,
    paddingVertical: 20,
    borderRadius: 25,
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 8,
    borderWidth: 3,
    borderColor: '#fff',
  },
  wakeWordDetectedText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    letterSpacing: 2,
  },
  wakeWordDetectedSubtext: {
    color: '#fff',
    fontSize: 14,
    textAlign: 'center',
    marginTop: 5,
    opacity: 0.9,
  },
});

