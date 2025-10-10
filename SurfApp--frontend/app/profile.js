import React, { useContext } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, TextInput } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context'; 
import { UserContext } from '../context/UserContext';

const ProfileScreen = () => {
  const { userPreferences, updatePreferences } = useContext(UserContext);
  
  const skillOptions = ['Beginner', 'Intermediate', 'Advanced'];
  const tideOptions = ['Any', 'High', 'Mid', 'Low'];
  const boardOptions = ['Shortboard', 'Longboard', 'Soft-top'];

  // Handles updates for numeric inputs (min/max wave height)
  const handleNumericChange = (key, value) => {
    const num = parseFloat(value);
    if (!isNaN(num) && num >= 0) {
        updatePreferences({ [key]: num });
    } else if (value === '') {
        updatePreferences({ [key]: 0 }); 
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView style={styles.container}>
        <Text style={styles.header}>My Surfer Profile</Text>
        <Text style={styles.subHeader}>Define your preferences for personalized recommendations.</Text>

        {/* 1. Skill Level Selector */}
        <Text style={styles.label}>1. Skill Level:</Text>
        <View style={styles.buttonGroup}>
          {skillOptions.map(skill => (
            <TouchableOpacity
              key={skill}
              style={[styles.button, userPreferences.skillLevel === skill && styles.selectedButton]}
              onPress={() => updatePreferences({ skillLevel: skill })}
            >
              <Text style={[styles.buttonText, userPreferences.skillLevel === skill && styles.selectedButtonText]}>{skill}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* 2. Wave Height Preference (Numeric Inputs) */}
        <Text style={styles.label}>2. Preferred Wave Height (meters):</Text>
        <View style={styles.inputGroup}>
          <TextInput
            style={styles.input}
            value={String(userPreferences.minWaveHeight)} 
            onChangeText={(text) => handleNumericChange('minWaveHeight', text)}
            keyboardType="numeric"
            placeholder="Min (e.g., 0.5)"
          />
          <Text style={styles.inputSeparator}>to</Text>
          <TextInput
            style={styles.input}
            value={String(userPreferences.maxWaveHeight)}
            onChangeText={(text) => handleNumericChange('maxWaveHeight', text)}
            keyboardType="numeric"
            placeholder="Max (e.g., 2.0)"
          />
        </View>
        
        {/* 3. Tide Preference */}
        <Text style={styles.label}>3. Preferred Tide:</Text>
        <View style={styles.buttonGroup}>
          {tideOptions.map(tide => (
            <TouchableOpacity
              key={tide}
              style={[styles.smallButton, userPreferences.tidePreference === tide && styles.selectedButton]}
              on onPress={() => updatePreferences({ tidePreference: tide })}
            >
              <Text style={[styles.buttonText, userPreferences.tidePreference === tide && styles.selectedButtonText]}>{tide}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* 4. Board Type */}
        <Text style={styles.label}>4. Current Board Type:</Text>
        <View style={styles.buttonGroup}>
          {boardOptions.map(board => (
            <TouchableOpacity
              key={board}
              style={[styles.smallButton, userPreferences.boardType === board && styles.selectedButton]}
              onPress={() => updatePreferences({ boardType: board })}
            >
              <Text style={[styles.buttonText, userPreferences.boardType === board && styles.selectedButtonText]}>{board}</Text>
            </TouchableOpacity>
          ))}
        </View>

        <View style={{ height: 50 }} />
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#f0f8ff' },
  container: { flex: 1, padding: 20 },
  header: { fontSize: 24, fontWeight: 'bold', textAlign: 'center', marginBottom: 10, color: '#007bff' },
  subHeader: { fontSize: 14, textAlign: 'center', marginBottom: 25, color: '#555' },
  label: { fontSize: 16, fontWeight: 'bold', marginTop: 15, marginBottom: 8 },
  
  buttonGroup: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'flex-start', marginBottom: 10 },
  button: {
    backgroundColor: 'white',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#007bff',
    marginRight: 10,
    marginBottom: 10,
  },
  smallButton: {
    backgroundColor: 'white',
    padding: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#007bff',
    marginRight: 8,
    marginBottom: 8,
  },
  selectedButton: { backgroundColor: '#007bff' },
  buttonText: { textAlign: 'center', fontSize: 16, color: '#007bff' },
  selectedButtonText: { color: 'white' },

  inputGroup: { flexDirection: 'row', alignItems: 'center', marginBottom: 15 },
  input: {
    flex: 1,
    backgroundColor: 'white',
    padding: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ccc',
    textAlign: 'center',
    fontSize: 16,
  },
  inputSeparator: { marginHorizontal: 10, fontSize: 16, fontWeight: 'bold' },
});

export default ProfileScreen;