const express = require('express');
const cors = require('cors');
// Import the child_process module to run the Python script
const { spawn } = require('child_process'); 
const app = express();
const PORT = 3000;

// Set the path to your Python executable and script
const PYTHON_EXECUTABLE = 'python'; // Use 'python' or 'python3' depending on your OS setup
const ML_SCRIPT_PATH = '../surfapp--ml-engine/predict_service.py'; // Path to the new Python file

// Enable CORS
app.use(cors({
    origin: 'http://10.0.2.2:8081', // Updated to 10.0.2.2 for Android emulator
}));
app.use(express.json());

// --- Core API Endpoint: Replaced with Python Call ---
app.get('/api/spots', (req, res) => {
    const skillLevel = req.query.skill || 'Beginner';

    // 1. Spawn a Python process and pass the skill level as an argument
    const pythonProcess = spawn(PYTHON_EXECUTABLE, [ML_SCRIPT_PATH, skillLevel]);

    let dataString = '';
    let errorString = '';

    // 2. Capture output from the Python script (JSON data)
    pythonProcess.stdout.on('data', (data) => {
        dataString += data.toString();
    });

    // 3. Capture errors from the Python script
    pythonProcess.stderr.on('data', (data) => {
        errorString += data.toString();
    });

    // 4. Handle process close/exit
    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            console.error(`Python script exited with code ${code}. Error: ${errorString}`);
            return res.status(500).json({ 
                error: 'ML prediction failed. Check Python logs.',
                details: errorString 
            });
        }

        try {
            const result = JSON.parse(dataString);
            // Success: Send the predicted and ranked spots back to the frontend
            res.json(result); 
        } catch (error) {
            console.error('Failed to parse Python output:', error);
            res.status(500).json({ error: 'Invalid data format from ML engine.' });
        }
    });
});

// Endpoint for fetching 7-day chart data (kept as mock for now, will be updated later)
app.get('/api/forecast-chart', (req, res) => {
    const chartData = {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        datasets: [{ data: [1.2, 1.5, 1.3, 2.0, 2.2, 1.8, 1.6] }],
    };
    res.json(chartData);
});


// Start the API Gateway
app.listen(PORT, () => {
    console.log(`API Gateway running on http://10.0.2.2:${PORT}`);
    console.log(`ML Engine connected at: ${ML_SCRIPT_PATH}`);
});