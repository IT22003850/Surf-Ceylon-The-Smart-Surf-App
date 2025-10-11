const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const app = express();
const PORT = 3000;

// --- Configuration ---
// Make sure these paths are correct for your environment
const PYTHON_EXECUTABLE = '../surfapp--ml-engine/venv/Scripts/python.exe'; 
const ML_SCRIPT_PATH = '../surfapp--ml-engine/predict_service.py'; 

// --- MODEL 2: ADVANCED SUITABILITY SCORING ALGORITHM ---
const calculateSuitability = (predictions, preferences, spotRegion) => {
    // 1. Parse and validate inputs from the user's profile and Model 1's predictions
    const { skillLevel, boardType, tidePreference } = preferences;
    const minWaveHeight = parseFloat(preferences.minWaveHeight) || 0.5;
    const maxWaveHeight = parseFloat(preferences.maxWaveHeight) || 2.5;
    const { waveHeight, wavePeriod, windSpeed, windDirection, tide } = predictions;

    let score = 100; // Start with a perfect score and deduct points based on rules

    // 2. Apply Scoring Rules

    // --- Rule: Wave Height vs. Skill Level (Safety & Challenge) ---
    if (skillLevel === 'Beginner') {
        if (waveHeight > 1.5) score -= 60; // Too big
        else if (waveHeight > 1.0) score -= 30;
    } else if (skillLevel === 'Intermediate') {
        if (waveHeight < 0.8) score -= 20; // Too small
        if (waveHeight > 2.5) score -= 40; // Too big
    } else if (skillLevel === 'Advanced') {
        if (waveHeight < 1.5) score -= 30; // Too small
    }
    
    // --- Rule: Wave Height vs. User's Explicit Preference ---
    if (waveHeight < minWaveHeight || waveHeight > maxWaveHeight) {
        score -= 25; // Penalize if outside the user's desired range
    }
    
    // --- Rule: Wave Period (Power & Quality) ---
    if (boardType === 'Shortboard' && wavePeriod < 9) score -= 20; // Short period is weak for shortboards
    if (boardType !== 'Shortboard' && wavePeriod > 12) score -= 15; // Very powerful swell can be hard on longboards

    // --- Rule: Wind Conditions ---
    if (windSpeed > 25) score -= 50; // Heavy onshore/choppy conditions
    else if (windSpeed > 15) score -= 25;
    
    // TODO: This is a simplified offshore wind check. A more advanced version
    // would have the exact offshore direction for each specific surf spot.
    const isOffshoreForEastCoast = (spotRegion === 'East Coast' && windDirection > 240 && windDirection < 300);
    const isOffshoreForSouthCoast = (spotRegion === 'South Coast' && windDirection > 330 || windDirection < 30);
    if (!isOffshoreForEastCoast && !isOffshoreForSouthCoast) {
        score -= 30; // Onshore/cross-shore wind penalty
    }

    // --- Rule: Tide Preference ---
    if (tidePreference !== 'Any' && tide.status !== tidePreference) {
        score -= 15;
    }

    // --- Rule: Monsoon Season (Critical for Sri Lanka) ---
    const currentMonth = new Date().getMonth() + 1; // January is 1, December is 12
    const isEastCoastSeason = currentMonth >= 4 && currentMonth <= 10; // Approx. April to October

    if (spotRegion === 'East Coast' && !isEastCoastSeason) score -= 60; // Heavy penalty for off-season
    if (spotRegion === 'South Coast' && isEastCoastSeason) score -= 60; // Heavy penalty for off-season

    // 3. Final Score: Ensure it's clamped between 0 and 100
    return Math.max(0, Math.min(100, score));
};

// --- API Endpoints ---
app.use(cors());
app.use(express.json());

// Main endpoint for getting ranked surf spot recommendations
app.get('/api/spots', (req, res) => {
    const userPreferences = req.query; 
    
    // Spawn the Python process to run Model 1. It no longer needs user input.
    const pythonProcess = spawn(PYTHON_EXECUTABLE, [ML_SCRIPT_PATH]);

    let pythonOutput = '';
    let pythonError = '';

    pythonProcess.stdout.on('data', (data) => {
        pythonOutput += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        pythonError += data.toString();
        console.log(`[PYTHON LOG]: ${data.toString().trim()}`);
    });

    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            console.error(`Python script failed. Code: ${code}. Error: ${pythonError}`);
            return res.status(500).json({ 
                error: 'The ML prediction engine failed to run.',
                details: pythonError 
            });
        }

        try {
            // The raw JSON output from Model 1 (predict_service.py)
            const model1Result = JSON.parse(pythonOutput);
            const spotsWithPredictions = model1Result.spots;
            
            // Apply Model 2 (Suitability Scoring) to each spot
            const finalRankedSpots = spotsWithPredictions.map(spot => {
                const suitabilityScore = calculateSuitability(spot.forecast, userPreferences, spot.region);
                return { ...spot, suitability: suitabilityScore };
            });
            
            // Sort the final list from highest to lowest suitability
            finalRankedSpots.sort((a, b) => b.suitability - a.suitability);

            res.json({ spots: finalRankedSpots });
            
        } catch (error) {
            console.error('Error processing Python output or scoring:', error);
            res.status(500).json({ error: 'Internal server error while generating recommendations.', details: error.message });
        }
    });
});

// Mock endpoint for the 7-day forecast chart
app.get('/api/forecast-chart', (req, res) => {
    const chartData = {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        datasets: [{ data: [1.2, 1.5, 1.3, 2.0, 2.2, 1.8, 1.6] }],
    };
    res.json(chartData);
});

// Start the server
app.listen(PORT, () => {
    console.log(`Surf Ceylon Backend running on http://localhost:${PORT}`);
});