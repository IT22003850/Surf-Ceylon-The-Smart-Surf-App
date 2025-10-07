import React, { useEffect } from 'react';
import { Tabs } from 'expo-router';
import { UserProvider } from '../context/UserContext';
import * as Font from 'expo-font'; // Import Font
import { Ionicons } from '@expo/vector-icons'; // Import a sample Icon set

// NOTE: We need to hide the splash screen once fonts are loaded
import * as SplashScreen from 'expo-splash-screen'; 
// Prevent the splash screen from auto-hiding
SplashScreen.preventAutoHideAsync();

// NO MAPBOX CODE SHOULD BE IN THIS FILE

export default function AppLayout() {
  const [fontsLoaded, fontError] = Font.useFonts(Ionicons.font);

  // Hide the splash screen once fonts are loaded or an error occurs
  useEffect(() => {
    if (fontsLoaded || fontError) {
      SplashScreen.hideAsync();
    }
  }, [fontsLoaded, fontError]);

  if (!fontsLoaded && !fontError) {
    // Return an empty view while waiting for fonts to load
    return null; 
  }

  return (
    <UserProvider>
      <Tabs screenOptions={{ tabBarActiveTintColor: '#007bff' }}> 
        <Tabs.Screen 
          name="index" 
          options={{ 
            title: 'Home',
            tabBarIcon: ({ color, size }) => (
              <Ionicons name="home" size={size} color={color} />
            ),
          }} 
        />
        <Tabs.Screen 
          name="(spots)" 
          options={{ 
            title: 'Spots', 
            headerShown: false,
            tabBarIcon: ({ color, size }) => (
              <Ionicons name="location-sharp" size={size} color={color} />
            ),
          }} 
        />
        <Tabs.Screen 
          name="map" 
          options={{ 
            title: 'Map',
            tabBarIcon: ({ color, size }) => (
              <Ionicons name="map" size={size} color={color} />
            ),
          }} 
        />
        <Tabs.Screen 
          name="profile" 
          options={{ 
            title: 'Profile',
            tabBarIcon: ({ color, size }) => (
              <Ionicons name="person" size={size} color={color} />
            ),
          }} 
        />
      </Tabs>
    </UserProvider>
  );
}