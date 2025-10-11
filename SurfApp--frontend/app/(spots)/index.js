import { UserContext } from '../../context/UserContext';
import { getSpotsData } from '../../data/surfApi'; 
import SpotCard from '../../components/SpotCard';
import React, { useContext, useState, useEffect } from 'react';
import { FlatList, StyleSheet, ActivityIndicator, View, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Link } from 'expo-router';

const SpotsListScreen = () => {
  // --- FIX #1: Get the entire userPreferences object from the context ---
  const { userPreferences } = useContext(UserContext);
  const [spots, setSpots] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSpots = async () => {
      try {
        setLoading(true);
        // --- FIX #2: Pass the complete userPreferences object to the API call ---
        const data = await getSpotsData(userPreferences);
        setSpots(data);
      } catch (e) {
        console.error("Error fetching spots for list screen:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchSpots();
  // --- FIX #3: The useEffect hook now depends on the entire object to refetch data when any preference changes ---
  }, [userPreferences]);

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007bff" />
        <Text style={{ marginTop: 10 }}>Loading full list of spots...</Text>
      </View>
    );
  }

  if (spots.length === 0) {
      return (
          <SafeAreaView style={styles.container}>
              <Text style={styles.noSpotsText}>No surf spots available right now.</Text>
          </SafeAreaView>
      );
  }

  return (
    <SafeAreaView style={styles.container}>
      <FlatList
        data={spots}
        keyExtractor={item => item.id}
        renderItem={({ item }) => (
          <Link href={{ pathname: "/(spots)/detail", params: { spot: JSON.stringify(item) } }} asChild>
            <SpotCard spot={item} />
          </Link>
        )}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#fff' },
  noSpotsText: { textAlign: 'center', marginTop: 20, fontSize: 18, color: '#888' },
});

export default SpotsListScreen;