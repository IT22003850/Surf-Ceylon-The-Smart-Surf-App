import React, { useContext } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native'; 
import { SafeAreaView } from 'react-native-safe-area-context'; // CORRECT: import from safe-area-context
import { UserContext } from '../context/UserContext';

const ProfileScreen = () => {
  const { skillLevel, setSkillLevel } = useContext(UserContext);
  const skills = ['Beginner', 'Intermediate', 'Advanced'];

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.header}>Select Your Skill Level</Text>
      <View>
        {skills.map(skill => (
          <TouchableOpacity
            key={skill}
            style={[styles.button, skillLevel === skill && styles.selectedButton]}
            onPress={() => setSkillLevel(skill)}
          >
            <Text style={[styles.buttonText, skillLevel === skill && styles.selectedButtonText]}>{skill}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: '#f0f8ff' },
  header: { fontSize: 22, fontWeight: 'bold', textAlign: 'center', marginBottom: 30 },
  button: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#007bff',
    marginBottom: 15,
  },
  selectedButton: {
    backgroundColor: '#007bff',
  },
  buttonText: {
    textAlign: 'center',
    fontSize: 18,
    color: '#007bff',
  },
  selectedButtonText: {
    color: 'white',
  },
});

export default ProfileScreen;