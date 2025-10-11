import React, { useContext } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { UserContext } from '../context/UserContext';

const ProfileScreen = () => {
  const { userPreferences, setUserPreferences } = useContext(UserContext);

  const handleUpdate = (key, value) => {
    setUserPreferences(prev => ({ ...prev, [key]: value }));
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.title}>Profile</Text>
        <Text style={styles.subtitle}>Define your preferences for personalized recommendations.</Text>

        {/* Skill Level */}
        <View style={styles.preferenceBlock}>
          <Text style={styles.label}>1. Skill Level:</Text>
          <View style={styles.optionsContainer}>
            {['Beginner', 'Intermediate', 'Advanced'].map(level => (
              <TouchableOpacity
                key={level}
                style={[styles.button, userPreferences.skillLevel === level && styles.selectedButton]}
                onPress={() => handleUpdate('skillLevel', level)}
              >
                <Text style={[styles.buttonText, userPreferences.skillLevel === level && styles.selectedButtonText]}>{level}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Wave Height */}
        <View style={styles.preferenceBlock}>
          <Text style={styles.label}>2. Preferred Wave Height (meters):</Text>
          <View style={styles.waveHeightContainer}>
            <TextInput
              style={styles.input}
              value={String(userPreferences.minWaveHeight)}
              onChangeText={text => handleUpdate('minWaveHeight', text)}
              // --- THIS IS THE FIX ---
              keyboardType="numeric" 
            />
            <Text style={styles.label}> to </Text>
            <TextInput
              style={styles.input}
              value={String(userPreferences.maxWaveHeight)}
              onChangeText={text => handleUpdate('maxWaveHeight', text)}
              // --- THIS IS THE FIX ---
              keyboardType="numeric"
            />
          </View>
        </View>

        {/* Tide */}
        <View style={styles.preferenceBlock}>
          <Text style={styles.label}>3. Preferred Tide:</Text>
          <View style={styles.optionsContainer}>
            {['Any', 'High', 'Mid', 'Low'].map(tide => (
              <TouchableOpacity
                key={tide}
                style={[styles.button, userPreferences.tidePreference === tide && styles.selectedButton]}
                onPress={() => handleUpdate('tidePreference', tide)}
              >
                <Text style={[styles.buttonText, userPreferences.tidePreference === tide && styles.selectedButtonText]}>{tide}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Board Type */}
        <View style={styles.preferenceBlock}>
          <Text style={styles.label}>4. Current Board Type:</Text>
          <View style={styles.optionsContainer}>
            {['Shortboard', 'Longboard', 'Soft-top'].map(board => (
              <TouchableOpacity
                key={board}
                style={[styles.button, userPreferences.boardType === board && styles.selectedButton]}
                onPress={() => handleUpdate('boardType', board)}
              >
                <Text style={[styles.buttonText, userPreferences.boardType === board && styles.selectedButtonText]}>{board}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9f9f9' },
  scrollContent: { padding: 20 },
  title: { fontSize: 28, fontWeight: 'bold', marginBottom: 10 },
  subtitle: { fontSize: 16, color: '#666', marginBottom: 30 },
  preferenceBlock: { marginBottom: 25 },
  label: { fontSize: 18, fontWeight: '500', marginBottom: 10 },
  optionsContainer: { flexDirection: 'row', flexWrap: 'wrap' },
  button: { 
    backgroundColor: '#fff', 
    paddingVertical: 10, 
    paddingHorizontal: 20, 
    borderRadius: 20, 
    margin: 5,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  selectedButton: { backgroundColor: '#007bff', borderColor: '#007bff' },
  buttonText: { color: '#007bff', fontSize: 16 },
  selectedButtonText: { color: '#fff' },
  waveHeightContainer: { flexDirection: 'row', alignItems: 'center' },
  input: {
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 10,
    fontSize: 16,
    width: 80,
    textAlign: 'center',
  },
});

export default ProfileScreen;