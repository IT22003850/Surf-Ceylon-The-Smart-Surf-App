import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { useLocalSearchParams, Stack } from 'expo-router';
import ForecastChart from '../../components/ForecastChart';

const SpotDetailScreen = () => {
  const params = useLocalSearchParams();
  let spot = null;
  try {
    spot = params && params.spot ? JSON.parse(params.spot) : null;
  } catch (e) {
    console.warn('Failed to parse spot param from navigation', e);
  }

  if (!spot) {
    return (
      <>
        <Stack.Screen options={{ title: 'Spot Details' }} />
        <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
          <Text>Spot details could not be loaded.</Text>
        </View>
      </>
    );
  }

  // Safely access nested forecast data
  const forecast = spot.forecast || {};
  const wind = forecast.wind || {};
  const tide = forecast.tide || {};

  return (
    <>
      <Stack.Screen options={{ title: spot.name }} />
      <ScrollView style={styles.container}>
        <Text style={styles.header}>{spot.name}</Text>
        <Text style={styles.regionHeader}>{spot.region}</Text>
        
        <View style={styles.detailsContainer}>
          <Text style={styles.detailText}>Suitability Score: {spot.suitability.toFixed(0)}%</Text>
          <Text style={styles.detailText}>Wave: {forecast.waveHeight}m @ {forecast.wavePeriod}s</Text>
          <Text style={styles.detailText}>Wind: {forecast.windSpeed} kph from {forecast.windDirection}°</Text>
          <Text style={styles.detailText}>Tide: {tide.status}</Text>
        </View>
        
        <Text style={styles.chartHeader}>7-Day Wave Forecast (m)</Text>
        <ForecastChart />
      </ScrollView>
    </>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9f9f9',
    padding: 16,
  },
  header: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#111',
    textAlign: 'center',
  },
  regionHeader: {
    fontSize: 18,
    color: '#666',
    textAlign: 'center',
    marginBottom: 20,
  },
  detailsContainer: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: '#eee',
  },
  detailText: {
    fontSize: 16,
    marginBottom: 10,
    color: '#444',
  },
  chartHeader: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
    textAlign: 'center',
  },
});

export default SpotDetailScreen;