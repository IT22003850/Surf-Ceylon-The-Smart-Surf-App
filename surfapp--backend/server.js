// surfapp--backend/server.js (API Gateway)
const express = require('express');
const cors = require('cors');

// --- MOCK DATA/LOGIC (TEMPORARY: Copied from frontend/data/mockData.js) ---
// This will be replaced by API calls (Surfline, OpenWeather, NOAA) and ML logic (Random Forest) in Phase 2
const surfSpots = [
  { id: '1', name: 'Arugam Bay', region: 'East Coast', coords: [81.829, 6.843] },
  { id: '2', name: 'Weligama', region: 'South Coast', coords: [80.426, 5.972] },
  { id: '3', name: 'Midigama', region: 'South Coast', coords: [80.383, 5.961] },
  { id: '4', name: 'Hiriketiya', region: 'South Coast', coords: [80.686, 5.976] },
  { id: '5', name: 'Okanda', region: 'East Coast', coords: [81.657, 6.660] },
];

const generateForecast = (spotId) => {
  const now = new Date();
  const waveHeight = (1 + Math.sin(now.getHours() + parseInt(spotId)) * 0.5).toFixed(1);
  const windSpeed = (5 + Math.cos(now.getHours() + parseInt(spotId)) * 3).toFixed(0);
  const tide = Math.sin(now.getHours() * 0.5 + parseInt(spotId)) > 0 ? 'High' : 'Low';

  return {
    waveHeight: parseFloat(waveHeight),
    wind: { speed: parseInt(windSpeed), direction: 'Offshore' },
    tide: { status: tide, next: 'Low in 3h' },
  };
};

const calculateSuitability = (forecast, skillLevel) => {
  let score = 100;
  const { waveHeight } = forecast;

  if (skillLevel === 'Beginner') {
    if (waveHeight > 1.5) score -= 60;
    else if (waveHeight > 1.0) score -= 30;
  } else if (skillLevel === 'Intermediate') {
    if (waveHeight < 1.0) score -= 20;
    if (waveHeight > 2.5) score -= 40;
  } else if (skillLevel === 'Advanced') {
    if (waveHeight < 1.8) score -= 30;
  }

  return Math.max(0, Math.min(100, score));
};

const getSpotsData = (skillLevel) => {
  return surfSpots.map(spot => {
    const forecast = generateForecast(spot.id);
    const suitability = calculateSuitability(forecast, skillLevel);
    return { ...spot, forecast, suitability };
  }).sort((a, b) => b.suitability - a.suitability);
};

// --- END MOCK DATA/LOGIC ---

const app = express();
const PORT = 3000;

// Enable CORS for frontend communication
app.use(cors({
    origin: 'http://localhost:8081', // Allow requests from your Expo dev server
}));
app.use(express.json());

// Main Endpoint (FR-011, FR-012): Get all spots, ranked by suitability
app.get('/api/spots', (req, res) => {
    // Extract skill level from query parameters (from the frontend's UserContext)
    const skillLevel = req.query.skill || 'Beginner';

    try {
        const spots = getSpotsData(skillLevel); // This is where ML-processed data will eventually come from
        res.json({ spots });
    } catch (error) {
        console.error('Error fetching spots:', error);
        res.status(500).json({ error: 'Failed to retrieve surf spots.' });
    }
});

// Simple endpoint for fetching 7-day chart data
app.get('/api/forecast-chart', (req, res) => {
    // This is the mock for the 7-day forecast graph data
    const chartData = {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        datasets: [{ data: [1.2, 1.5, 1.3, 2.0, 2.2, 1.8, 1.6] }],
    };
    res.json(chartData);
});


// Start the API Gateway
app.listen(PORT, () => {
    console.log(`API Gateway running on http://localhost:${PORT}`);
    console.log("To run the frontend, ensure your Expo server is running.");
    console.log("Note: This is Step 1. The mock logic must be replaced with real data fetching and ML in Phase 2.");
});