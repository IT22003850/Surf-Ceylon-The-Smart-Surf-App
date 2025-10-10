const API_BASE_URL = 'http://10.0.2.2:3000/api';

/**
 * Fetches the list of surf spots, ranked by suitability based on the user's preferences.
 * @param {Object} preferences - The full user preferences object from UserContext.
 * @returns {Array<Object>} An array of spot data with forecast and suitability.
 */
export async function getSpotsData(preferences) { 
  try {
    // Convert preferences object into URL query string (e.g., skillLevel=Beginner&minWaveHeight=0.5)
    const queryString = new URLSearchParams(preferences).toString(); 
    
    const response = await fetch(`${API_BASE_URL}/spots?${queryString}`); 
    
    if (!response.ok) {
      throw new Error(`API call failed with status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.spots;

  } catch (error) {
    console.error("Error fetching spots from API:", error);
    return []; 
  }
}

/**
 * Fetches the 7-day wave forecast data for the chart.
 * This is currently a mock endpoint on the Node.js server.
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
    return { labels: [], datasets: [{ data: [0] }] };
  }
}

/**
 * Static spot data used primarily for the Mapbox marker coordinates.
 */
export const surfSpots = [
  { id: '1', name: 'Arugam Bay', region: 'East Coast', coords: [81.829, 6.843] },
  { id: '2', name: 'Weligama', region: 'South Coast', coords: [80.426, 5.972] },
  { id: '3', name: 'Midigama', region: 'South Coast', coords: [80.383, 5.961] },
  { id: '4', name: 'Hiriketiya', region: 'South Coast', coords: [80.686, 5.976] },
  { id: '5', 'name': 'Okanda', region: 'East Coast', coords: [81.657, 6.660] },
];