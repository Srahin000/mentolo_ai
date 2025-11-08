/**
 * HoloMentor Mobile - Main App Entry Point
 * React Native app with Expo for fast iteration
 */

import React from 'react';
import { StyleSheet, View } from 'react-native';
import ARPlaceholder from './ARPlaceholder';

export default function App() {
  return (
    <View style={styles.container}>
      <ARPlaceholder />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});

