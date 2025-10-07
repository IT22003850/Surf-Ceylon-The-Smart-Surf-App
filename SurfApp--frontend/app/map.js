// it22003850/surfapp--frontend/SurfApp--frontend-e324eabe43c305ffac4f3010e13f33c56e3743db/app/map.js
import React, { useContext } from 'react';
import { View, StyleSheet, Platform, Text } from 'react-native';
import { UserContext } from '../context/UserContext';
import { surfSpots } from '../data/surfApi'; // CHANGED: Import surfSpots from the new API file

// This structure handles web and native platforms differently
let MapView, Camera, PointAnnotation;
if (Platform.OS !== 'web') {
  // For native (Android/iOS), import the library and set the token
  const Mapbox = require('@rnmapbox/maps');
  MapView = Mapbox.MapView;
  Camera = Mapbox.Camera;
  PointAnnotation = Mapbox.PointAnnotation;
  Mapbox.setAccessToken(
    'pk.eyJ1IjoiaXQyMjAwMzg1MCIsImEiOiJjbWZ4cTdlaDUwOWVtMmtzYmVuczJkdHB3In0.DHQYc1JaOBNIztXu38ihig'
  );
}

const MapScreen = () => {
  const { skillLevel } = useContext(UserContext);
  // NOTE: We use the static surfSpots array for map markers (coordinates), 
  // not the full getSpotsData which fetches ranked data.

  // If on web, show a placeholder. If native, show the map.
  if (Platform.OS === 'web') {
    return (
      <View style={styles.container}>
        <Text>Map is available on the mobile app.</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <MapView style={styles.map}>
        <Camera
          zoomLevel={7}
          centerCoordinate={[80.7718, 7.8731]} // Center of Sri Lanka
        />
        {surfSpots.map(spot => ( // CHANGED: Use surfSpots from the new API file
          <PointAnnotation
            key={spot.id}
            id={spot.id}
            coordinate={spot.coords}
          />
        ))}
      </MapView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    alignItems: 'center', 
    justifyContent: 'center' 
  },
  map: { 
    flex: 1, 
    width: '100%' 
  },
});

export default MapScreen;