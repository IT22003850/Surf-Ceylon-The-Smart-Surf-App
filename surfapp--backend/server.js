const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const app = express();
const PORT = 3000;

// --- CONFIGURATION ---
const PYTHON_EXECUTABLE = '../surfapp--ml-engine/venv/Scripts/python.exe'; 
const ML_SCRIPT_PATH = '../surfapp--ml-engine/predict_service.py';

// --- 🎯 FINAL FIX: IN-MEMORY CACHE FOR MOCK DATA ---
const cache = {
    data: null,
    timestamp: null,
    // Cache data for 60 seconds to ensure consistency across screen navigations
    CACHE_DURATION_MS: 60 * 1000, 
};

// --- MODEL 2: SUITABILITY CALCULATION (UNCHANGED) ---
const calculateSuitability = (predictions, preferences, spotRegion) => {
    const { skillLevel, boardType, tidePreference } = preferences;
    const minWaveHeight = parseFloat(preferences.minWaveHeight) || 0.5;
    const maxWaveHeight = parseFloat(preferences.maxWaveHeight) || 2.5;
    const { waveHeight, wavePeriod, windSpeed, windDirection, tide } = predictions;

    let score = 100;

    // Rules for scoring (as we defined before)
    if (skillLevel === 'Beginner' && waveHeight > 1.2) score -= 50;
    if (skillLevel === 'Intermediate' && (waveHeight < 0.8 || waveHeight > 2.5)) score -= 30;
    if (skillLevel === 'Advanced' && waveHeight < 1.5) score -= 40;
    if (waveHeight < minWaveHeight || waveHeight > maxWaveHeight) score -= 25;
    if (boardType === 'Shortboard' && wavePeriod < 9) score -= 20;
    if (boardType !== 'Shortboard' && wavePeriod > 12) score -= 15;
    if (windSpeed > 25) score -= 50;
    else if (windSpeed > 15) score -= 25;
    
    const isOffshoreForEastCoast = (spotRegion === 'East Coast' && windDirection > 240 && windDirection < 300);
    const isOffshoreForSouthCoast = (spotRegion === 'South Coast' && (windDirection > 330 || windDirection < 30));
    if (!isOffshoreForEastCoast && !isOffshoreForSouthCoast) {
        score -= 30;
    }

    if (tidePreference !== 'Any' && tide.status !== tidePreference) score -= 15;

    const currentMonth = new Date().getMonth() + 1;
    const isEastCoastSeason = currentMonth >= 4 && currentMonth <= 10;
    if (spotRegion === 'East Coast' && !isEastCoastSeason) score -= 60;
    if (spotRegion === 'South Coast' && isEastCoastSeason) score -= 60;

    return Math.max(0, Math.min(100, score));
};

// --- API Endpoints ---
app.use(cors());
app.use(express.json());

app.get('/api/spots', (req, res) => {
    const userPreferences = req.query;

    // --- CACHE LOGIC ---
    const now = Date.now();
    if (cache.data && cache.timestamp && (now - cache.timestamp < cache.CACHE_DURATION_MS)) {
        console.log("Serving request from cache.");
        // If fresh data exists in cache, use it immediately
        const spotsWithPredictions = cache.data;
        const finalRankedSpots = spotsWithPredictions.map(spot => ({
            ...spot,
            suitability: calculateSuitability(spot.forecast, userPreferences, spot.region),
        }));
        finalRankedSpots.sort((a, b) => b.suitability - a.suitability);
        return res.json({ spots: finalRankedSpots });
    }
    
    console.log("Cache is stale or empty. Fetching new data from Python script.");
    const pythonProcess = spawn(PYTHON_EXECUTABLE, [ML_SCRIPT_PATH]);

    let pythonOutput = '';
    let pythonError = '';

    pythonProcess.stdout.on('data', (data) => pythonOutput += data.toString());
    pythonProcess.stderr.on('data', (data) => {
        pythonError += data.toString();
        console.log(`[PYTHON LOG]: ${data.toString().trim()}`);
    });

    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            console.error(`Python script failed. Code: ${code}. Error: ${pythonError}`);
            return res.status(500).json({ error: 'ML prediction failed.' });
        }

        try {
            const model1Result = JSON.parse(pythonOutput);
            const spotsWithPredictions = model1Result.spots;
            
            // --- Store the new data in the cache ---
            cache.data = spotsWithPredictions;
            cache.timestamp = Date.now();
            console.log("Updated cache with new data.");

            const finalRankedSpots = spotsWithPredictions.map(spot => ({
                ...spot,
                suitability: calculateSuitability(spot.forecast, userPreferences, spot.region),
            }));
            
            finalRankedSpots.sort((a, b) => b.suitability - a.suitability);
            res.json({ spots: finalRankedSpots });
            
        } catch (error) {
            console.error('Error processing Python output or scoring:', error);
            res.status(500).json({ error: 'Internal server error.', details: error.message });
        }
    });
});

app.get('/api/forecast-chart', (req, res) => {
    const chartData = {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        datasets: [{ data: [1.2, 1.5, 1.3, 2.0, 2.2, 1.8, 1.6] }],
    };
    res.json(chartData);
});

app.listen(PORT, () => {
    console.log(`Surf Ceylon Backend running on http://localhost:${PORT}`);
});