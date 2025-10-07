// data/surfApi.js

const API_BASE_URL = 'http://10.0.2.2:3000/api';

/**
 * Fetches the list of surf spots, ranked by suitability based on the user's skill level.
 * This function communicates with the new API Gateway.
 * @param {string} skillLevel - The user's current skill level.
 * @returns {Array<Object>} An array of spot data with forecast and suitability.
 */
export async function getSpotsData(skillLevel) {
  try {
    const response = await fetch(`${API_BASE_URL}/spots?skill=${skillLevel}`);
    
    if (!response.ok) {
      throw new Error(`API call failed with status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.spots;

  } catch (error) {
    console.error("Error fetching spots from API:", error);
    // Fallback to empty array or a cached version if implemented later
    return []; 
  }
}

/**
 * Fetches the 7-day wave forecast data for the chart.
 * This is currently mocked on the backend.
 */
export async function get7DayForecast() {
  try {
    const response = await fetch(`${API_BASE_URL}/forecast-chart`);
    
    if (!response.ok) {
      throw new Error(`API call failed with status: ${response.status}`);
    }
    
    return await response.json();

  } catch (error) {
    console.error("Error fetching chart data from API:", error);
    // Return a default structure to prevent app crash
    return { labels: [], datasets: [{ data: [0] }] };
  }
}

/**
 * Gets the static spot data used primarily for the Mapbox marker coordinates.
 * This is deliberately kept static for now as coordinates don't change.
 * In Phase 2, this list will be fetched from a dedicated spot database.
 */
export const surfSpots = [
  { id: '1', name: 'Arugam Bay', region: 'East Coast', coords: [81.829, 6.843] },
  { id: '2', name: 'Weligama', region: 'South Coast', coords: [80.426, 5.972] },
  { id: '3', name: 'Midigama', region: 'South Coast', coords: [80.383, 5.961] },
  { id: '4', name: 'Hiriketiya', region: 'South Coast', coords: [80.686, 5.976] },
  { id: '5', name: 'Okanda', region: 'East Coast', coords: [81.657, 6.660] },
];