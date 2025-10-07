// app/(spots)/detail.js
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
    console.warn('Failed to parse spot param', e);
  }

  if (!spot) {
    return (
      <>
        <Stack.Screen options={{ title: 'Spot Details' }} />
        <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
          <Text>Spot details are not available.</Text>
        </View>
      </>
    );
  }

  return (
    <>
      <Stack.Screen options={{ title: spot.name }} />
      <ScrollView style={styles.container}>
        <Text style={styles.header}>{spot.name}</Text>
        <View style={styles.detailsContainer}>
          <Text style={styles.detailText}>Suitability: {spot.suitability.toFixed(0)}%</Text>
          <Text style={styles.detailText}>Wave Height: {spot.forecast.waveHeight}m</Text>
          <Text style={styles.detailText}>Wind: {spot.forecast.wind.speed} kph</Text>
          <Text style={styles.detailText}>Tide: {spot.forecast.tide.status}</Text>
        </View>
        <Text style={styles.chartHeader}>7-Day Wave Forecast (m)</Text>
        <ForecastChart />
      </ScrollView>
    </>
  );
};

export default SpotDetailScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 16,
  },
  header: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 12,
    color: '#222',
    textAlign: 'center',
  },
  detailsContainer: {
    marginBottom: 24,
    backgroundColor: '#f2f2f2',
    borderRadius: 8,
    padding: 16,
  },
  detailText: {
    fontSize: 16,
    marginBottom: 8,
    color: '#444',
  },
  chartHeader: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#222',
    textAlign: 'center',
  },
});
