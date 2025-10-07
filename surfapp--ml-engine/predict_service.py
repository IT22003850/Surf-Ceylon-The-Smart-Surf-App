# predict_service.py
import json
import random
import sys
from datetime import datetime
from math import sin, cos, pi

# --- Mock Data/Functions (To be replaced with real API and ML logic) ---

# This static spot list will eventually be fetched from MongoDB (Data Layer)
# It mirrors the data structure from your frontend, but will be enriched with metadata (reef, coordinates, etc.)
SURF_SPOTS = [
    {'id': '1', 'name': 'Arugam Bay', 'region': 'East Coast', 'coords': [81.829, 6.843]},
    {'id': '2', 'name': 'Weligama', 'region': 'South Coast', 'coords': [80.426, 5.972]},
    {'id': '3', 'name': 'Midigama', 'region': 'South Coast', 'coords': [80.383, 5.961]},
    {'id': '4', 'name': 'Hiriketiya', 'region': 'South Coast', 'coords': [80.686, 5.976]},
    {'id': '5', 'name': 'Okanda', 'region': 'East Coast', 'coords': [81.657, 6.660]},
]

# This simulates the ML Model Prediction (FR-006)
def run_ml_prediction(spot_id):
    """
    Simulates a call to a trained Random Forest model.
    In the real implementation, this would:
    1. Fetch real-time data from Surfline/OpenWeather/NOAA (FR-001, FR-002).
    2. Input features (wave height, wind, monsoon factor, reef) into the RF model.
    3. Output predicted conditions and a quality score.
    """
    now = datetime.now()
    
    # Dynamic mock based on hour and spot ID to simulate varying conditions
    seed = now.hour + int(spot_id)
    random.seed(seed)
    
    # Simulate Wave Height Prediction (FR-006: 95% accuracy target)
    wave_height = round(1.0 + sin(now.hour * 0.2 + int(spot_id)) * 0.8 + random.uniform(-0.1, 0.1), 1)
    wave_height = max(0.5, wave_height) # Keep a minimum wave height
    
    # Simulate Wind Speed/Direction
    wind_speed = random.randint(3, 15) 
    
    # Simulate Tide Status
    tide_status = 'High' if sin(now.hour * 0.5 + int(spot_id)) > 0 else 'Low'
    
    return {
        'waveHeight': float(wave_height),
        'wind': {'speed': wind_speed, 'direction': 'Offshore'},
        'tide': {'status': tide_status, 'next': 'TBD'} # Next tide prediction will be real in Phase 3
    }

# This implements the core Suitability Logic (FR-011)
def calculate_suitability(forecast, skill_level):
    """
    Applies logic to calculate a spot's suitability score based on forecast
    and the user's skill profile. This replaces the JS logic.
    """
    score = 100
    wave_height = forecast['waveHeight']

    # Logic based on proposal (Section 1.2, 1.3 - need for personalized recommendations)
    if skill_level == 'Beginner':
        if wave_height > 1.5: score -= 60
        elif wave_height > 1.0: score -= 30
    elif skill_level == 'Intermediate':
        if wave_height < 1.0: score -= 20
        if wave_height > 2.5: score -= 40
    elif skill_level == 'Advanced':
        if wave_height < 1.8: score -= 30

    return max(0, min(100, score))

# --- Main Service Function ---

def get_spots_with_predictions(skill_level):
    """Generates predictions and ranks spots."""
    predicted_spots = []
    
    for spot in SURF_SPOTS:
        # Step 1: Get the ML Prediction for the spot
        forecast = run_ml_prediction(spot['id'])
        
        # Step 2: Calculate Suitability (Recommendation Logic)
        suitability = calculate_suitability(forecast, skill_level)
        
        # Combine all data
        predicted_spots.append({
            **spot,
            'forecast': forecast,
            'suitability': suitability
        })
        
    # Sort by suitability descending (FR-012)
    predicted_spots.sort(key=lambda x: x['suitability'], reverse=True)
    return predicted_spots

# --- Execution Entry Point ---

if __name__ == '__main__':
    # The Node.js server will pass the skill level as a command-line argument
    if len(sys.argv) > 1:
        skill = sys.argv[1]
    else:
        skill = 'Beginner' 

    try:
        # This simulates fetching and processing live data
        results = get_spots_with_predictions(skill)
        
        # Return the results as a JSON string to the Node.js API via standard output
        print(json.dumps({'spots': results}))
        
    except Exception as e:
        # Print errors to standard error, which Node.js can capture
        sys.stderr.write(json.dumps({'error': str(e)}))
        sys.exit(1)