import { Stack } from 'expo-router';

export default function SpotsLayout() {
  return (
    <Stack>
      <Stack.Screen name="index" options={{ title: 'All Surf Spots' }} />
      <Stack.Screen name="detail" options={{ title: 'Spot Details' }} />
    </Stack>
  );
}