import json
import sys
import random
from datetime import datetime, timezone
from math import sin
import os
import joblib 
import numpy as np 
import pandas as pd # NEW IMPORT for Scikit-learn compatibility
from dotenv import load_dotenv
from pymongo import MongoClient
import requests

# --- Setup and Constants ---

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI") 
DB_NAME = 'surf_app_db'
COLLECTION_NAME = 'forecast_history'

# Path to the trained model file.
MODEL_FILENAME = 'random_forest_surf_model.joblib'
MODEL_PATH = os.path.join(os.path.dirname(__file__), MODEL_FILENAME)
FEATURE_NAMES = ['wind_speed', 'pressure'] # Features used in train_model.py

# Static spot data using stable COORDS instead of unstable city_name
SURF_SPOTS = [
    {'id': '1', 'name': 'Arugam Bay', 'region': 'East Coast', 'coords': [81.829, 6.843]},
    {'id': '2', 'name': 'Weligama', 'region': 'South Coast', 'coords': [80.426, 5.972]},
    {'id': '3', 'name': 'Midigama', 'region': 'South Coast', 'coords': [80.383, 5.961]}, 
    {'id': '4', 'name': 'Hiriketiya', 'region': 'South Coast', 'coords': [80.686, 5.976]}, 
    {'id': '5', 'name': 'Okanda', 'region': 'East Coast', 'coords': [81.657, 6.660]},
]


# --- Model Loading (Runs once when the script starts) ---
SURF_PREDICTOR = None
try:
    if os.path.exists(MODEL_PATH):
        SURF_PREDICTOR = joblib.load(MODEL_PATH)
        print("Trained Random Forest Model loaded successfully.", file=sys.stderr)
except Exception as e:
    SURF_PREDICTOR = None
    print(f"Error loading model: {e}. Running in simulation mode.", file=sys.stderr)


# --- DATABASE FUNCTIONS (FR-005) ---

def connect_to_mongodb():
    """Establishes connection to MongoDB Atlas."""
    if not MONGODB_URI:
        print("Error: MONGODB_URI is missing. Cannot connect to database.", file=sys.stderr)
        return None
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping') 
        return client.get_database(DB_NAME)
        
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}", file=sys.stderr)
        return None

def save_historical_data(spot_id, raw_data, prediction):
    """Saves a snapshot of raw API data and the resulting prediction to MongoDB (FR-005)."""
    db = connect_to_mongodb()
    
    if db is not None: 
        try:
            history_collection = db[COLLECTION_NAME]
            record = {
                'spot_id': spot_id,
                # Fixes the DeprecationWarning: use timezone-aware objects (datetime.UTC)
                'timestamp': datetime.now(timezone.utc), 
                'raw_data': raw_data,
                'prediction': prediction
            }
            history_collection.insert_one(record)
        except Exception as e:
            print(f"Error inserting record into MongoDB: {e}", file=sys.stderr)
    else:
        print("Warning: Skipping database save due to connection failure.", file=sys.stderr)


# --- API FETCH & ML Prediction ---

def fetch_real_time_weather(coords):
    """Fetches real-time wind/weather data from OpenWeather API using COORDS (FR-002)."""
    if not OPENWEATHER_API_KEY:
        print("Error: OPENWEATHER_API_KEY is missing.", file=sys.stderr)
        return None

    # CRITICAL FIX: Use lat/lon for API stability
    lon, lat = coords
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        response.raise_for_status() 
        data = response.json()
        
        # Data Cleaning/Extraction
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'wind_speed': data['wind'].get('speed'), # m/s
            'pressure': data['main'].get('pressure'),
            'temp': data['main'].get('temp'),
        }
    except requests.exceptions.RequestException as e:
        # Log 404/network errors gracefully
        print(f"Error fetching OpenWeather for coords {coords}: {e}", file=sys.stderr)
        return None


def run_ml_prediction(spot, fetched_weather):
    """
    Predicts wave height using the loaded Random Forest model (FR-006).
    """
    
    # Extract features, providing None default if missing from API response
    wind_speed_ms = fetched_weather.get('wind_speed')
    pressure = fetched_weather.get('pressure')
    
    if SURF_PREDICTOR and wind_speed_ms is not None and pressure is not None:
        # --- ML Model Prediction Path (FR-006) ---
        try:
            # 1. Prepare Features (Use DataFrame to pass FEATURE_NAMES - CRITICAL FIX)
            features_df = pd.DataFrame(
                [[wind_speed_ms, pressure]], 
                columns=FEATURE_NAMES 
            )
            
            # 2. Predict Wave Height 
            predicted_wave_height = SURF_PREDICTOR.predict(features_df)[0]
            predicted_wave_height = round(float(predicted_wave_height), 1)
            
            # Mock accuracy based on target (for demonstration)
            accuracy = f"{random.uniform(90, 95):.1f}%" 
            
        except Exception as e:
            # Fallback if prediction fails (e.g., bad model data)
            print(f"ML Model Prediction failed: {e}. Falling back to simulation.", file=sys.stderr)
            predicted_wave_height = random.uniform(0.5, 2.0)
            accuracy = f"{random.randint(60, 80)}%"

    else:
        # --- Fallback Simulation Path (if model/data is missing) ---
        wind_speed_safe = wind_speed_ms if wind_speed_ms is not None else random.uniform(3, 15)
        predicted_wave_height = 0.5 + (wind_speed_safe / 10) 
        predicted_wave_height = round(float(predicted_wave_height), 1)
        accuracy = f"{random.randint(60, 80)}%" 

    # Mock tide status 
    tide_status = 'High' if sin(datetime.now().hour * 0.5 + int(spot['id'])) > 0 else 'Low'
    
    return {
        'waveHeight': max(0.2, predicted_wave_height), 
        'wind': {'speed': round(wind_speed_ms * 3.6), 'direction': 'Offshore'}, 
        'tide': {'status': tide_status, 'next': 'TBD'},
        'accuracy_confidence': accuracy 
    }


def calculate_suitability(forecast, skill_level):
    """Applies the core recommendation logic (FR-011)."""
    score = 100
    wave_height = forecast['waveHeight']

    # Logic based on proposal
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
    predicted_spots = []
    
    for spot in SURF_SPOTS:
        # Step 1: Fetch Real-Time Data using coordinates
        fetched_weather = fetch_real_time_weather(spot['coords'])
        
        if fetched_weather is None:
            continue

        # Step 2: Run ML Prediction (FR-006)
        forecast = run_ml_prediction(spot, fetched_weather)
        
        # Step 3: Calculate Suitability (FR-011)
        suitability = calculate_suitability(forecast, skill_level)
        
        # Step 4: Save the historical record (FR-005)
        save_historical_data(spot['id'], fetched_weather, forecast) 
        
        # Combine all data for the Node.js API response
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
    # Argument extraction logic
    if len(sys.argv) > 1:
        skill = sys.argv[1]
    else:
        skill = 'Beginner' 

    try:
        # Run the full pipeline
        results = get_spots_with_predictions(skill)
        
        # Return success output as JSON
        print(json.dumps({'spots': results}))
        
    except Exception as e:
        # Log any unexpected errors to stderr for Node.js to catch
        sys.stderr.write(json.dumps({'error': str(e), 'traceback': str(e)}))
        sys.exit(1)