// SurfApp--frontend/app/index.js
import React, { useContext, useState, useEffect } from 'react';
import { Text, StyleSheet, ActivityIndicator, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context'; 
import { Link } from 'expo-router';
import { UserContext } from '../context/UserContext';
import { getSpotsData } from '../data/surfApi'; 
import SpotCard from '../components/SpotCard';

const HomeScreen = () => {
  const { userPreferences } = useContext(UserContext); // This part is correct
  const [spots, setSpots] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSpots = async () => {
      try {
        setLoading(true);
        const data = await getSpotsData(userPreferences); 
        setSpots(data);
      } catch (e) {
        console.error("Error fetching spots for home screen:", e);
      } finally {
        setLoading(false);
      }
    };
    
    fetchSpots();
  // --- THIS IS THE FIX ---
  // The useEffect will now re-run whenever the userPreferences object changes.
  }, [userPreferences]); 

  const topPick = spots[0];

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007bff" />
        <Text style={{ marginTop: 10 }}>Loading personalized spots...</Text>
      </View>
    );
  }

  if (!topPick) {
     return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.header}>Welcome, {userPreferences.skillLevel} Surfer!</Text>
        <Text style={styles.subHeader}>No spots found right now.</Text>
      </SafeAreaView>
     );
  }

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.header}>Welcome, {userPreferences.skillLevel} Surfer!</Text>
      <Text style={styles.subHeader}>{`Today's Top Recommendation`}</Text>
      
      <Link href={{ pathname: "/(spots)/detail", params: { spot: JSON.stringify(topPick) } }} asChild>
        <SpotCard spot={topPick} />
      </Link>
      
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 10, backgroundColor: '#f0f8ff' },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f0f8ff' },
  header: { fontSize: 24, fontWeight: 'bold', textAlign: 'center', marginVertical: 10 },
  subHeader: { fontSize: 18, color: '#555', textAlign: 'center', marginBottom: 15 },
});

export default HomeScreen;