// SurfApp--frontend/app/map.js

import React, { useState, useEffect, useContext } from 'react';
import { View, StyleSheet, ActivityIndicator, Text } from 'react-native';
import Mapbox from '@rnmapbox/maps';
import { UserContext } from '../context/UserContext';
import { getSpotsData } from '../data/surfApi';

// --- THIS IS THE FIX #1: ADD YOUR MAPBOX PUBLIC KEY HERE ---
// You must get this from your account at https://www.mapbox.com/
const MAPBOX_ACCESS_TOKEN = 'pk.eyJ1IjoiaXQyMjAwMzg1MCIsImEiOiJjbWZ4cTdlaDUwOWVtMmtzYmVuczJkdHB3In0.DHQYc1JaOBNIztXu38ihig'; 
Mapbox.setAccessToken(MAPBOX_ACCESS_TOKEN);

const MapScreen = () => {
  const { userPreferences } = useContext(UserContext);
  const [spots, setSpots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!MAPBOX_ACCESS_TOKEN || MAPBOX_ACCESS_TOKEN === 'YOUR_MAPBOX_PUBLIC_ACCESS_TOKEN') {
      setError('Mapbox Access Token is not configured. Please add it in app/map.js');
      setLoading(false);
      return;
    }

    const fetchAndSetSpots = async () => {
      try {
        setLoading(true);
        setError(null);
        // Uses the function updated in the previous step with the static data fallback
        const data = await getSpotsData(userPreferences);
        setSpots(data);
      } catch (error) {
        console.error("Error fetching spots for map:", error);
        setError('Failed to load spot data.');
      } finally {
        setLoading(false);
      }
    };
    fetchAndSetSpots();
  }, [userPreferences]);

  const getMarkerColor = (suitability) => {
    if (suitability > 75) return '#4caf50';
    if (suitability > 50) return '#ffc107';
    if (suitability > 25) return '#ff9800';
    return '#f44336';
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" />
        <Text>Loading Map and Personalized Spots...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={{color: 'red'}}>{error}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Mapbox.MapView style={styles.map}>
        <Mapbox.Camera
          zoomLevel={7}
          centerCoordinate={[80.7718, 7.8731]}
        />
        {spots.map(spot => {
          const lon = parseFloat(spot.coords[0]);
          const lat = parseFloat(spot.coords[1]);

          if (isNaN(lon) || isNaN(lat)) {
            console.warn(`Invalid coordinates for spot: ${spot.name}`);
            return null;
          }
          
          return (
            <Mapbox.PointAnnotation
              key={spot.id}
              id={spot.id}
              // Coordinates are correctly [Longitude, Latitude]
              coordinate={[lon, lat]} 
            >
              <View style={[styles.markerContainer, { backgroundColor: getMarkerColor(spot.suitability) }]}>
                <Text style={styles.markerText}>{spot.suitability.toFixed(0)}</Text>
              </View>
            </Mapbox.PointAnnotation>
          );
        })}
      </Mapbox.MapView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1 },
  map: { flex: 1 },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  markerContainer: {
    width: 35,
    height: 35,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    borderColor: 'white',
    borderWidth: 2,
    // ✅ FIX: Explicitly set zIndex to ensure custom marker views render on top
    zIndex: 99 
  },
  markerText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 12,
  },
});

export default MapScreen;