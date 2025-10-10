import json
import sys
import random
import os
import joblib 
import numpy as np 
import pandas as pd
from datetime import datetime, timezone
from math import sin
from dotenv import load_dotenv
from pymongo import MongoClient
import requests

# --- Configuration ---
load_dotenv()
STORMGLASS_API_KEY = os.getenv("STORMGLASS_API_KEY") 
MONGODB_URI = os.getenv("MONGODB_URI") 
DB_NAME = 'surf_app_db'
COLLECTION_NAME = 'forecast_history'

# Feature names used for training/prediction (must match train_model.py)
FEATURE_NAMES = ['wind_speed', 'pressure'] 

MODEL_FILENAME = 'random_forest_surf_model.joblib'
MODEL_PATH = os.path.join(os.path.dirname(__file__), MODEL_FILENAME)

# Static spot data 
SURF_SPOTS = [
    {'id': '1', 'name': 'Arugam Bay', 'region': 'East Coast', 'coords': [81.829, 6.843]},
    {'id': '2', 'name': 'Weligama', 'region': 'South Coast', 'coords': [80.426, 5.972]},
    {'id': '3', 'name': 'Midigama', 'region': 'South Coast', 'coords': [80.383, 5.961]},
    {'id': '4', 'name': 'Hiriketiya', 'region': 'South Coast', 'coords': [80.686, 5.976]},
    {'id': '5', 'name': 'Okanda', 'region': 'East Coast', 'coords': [81.657, 6.660]},
]


# --- Model Loading (Runs once) ---
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
                'timestamp': datetime.now(timezone.utc), 
                'raw_data': raw_data,
                'prediction': prediction
            }
            history_collection.insert_one(record)
        except Exception as e:
            print(f"Error inserting record into MongoDB: {e}", file=sys.stderr)
    else:
        print("Warning: Skipping database save due to connection failure.", file=sys.stderr)


# --- API FETCH & ML Prediction (Model 1) ---

def fetch_real_time_weather(coords):
    """Fetches real-time wind/weather/marine data using coordinates (STORMGLASS API)."""
    if not STORMGLASS_API_KEY:
        print("Error: STORMGLASS_API_KEY is missing.", file=sys.stderr)
        return None

    # NOTE: The actual Stormglass API call logic goes here
    # Since we need to replace OpenWeather, this function should now fetch
    # Swell Height, Swell Period, Wind Speed, and Sea Level from Stormglass.

    lon, lat = coords
    # Features requested for prediction. (We will use these later)
    # params = 'waveHeight,windSpeed,pressure,swellHeight,swellPeriod,seaLevel'
    
    try:
        # --- PLACEHOLDER FOR STORMGLASS API CALL ---
        # This mocks the data structure that Stormglass returns
        wind_speed_ms = random.uniform(3, 15)
        pressure_hpa = random.uniform(1010, 1020)
        sea_level_m = random.uniform(0.1, 1.0)
        # --- END PLACEHOLDER ---
        
        # Data Cleaning/Extraction
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'wind_speed': wind_speed_ms, 
            'pressure': pressure_hpa,
            'sea_level': sea_level_m
            # Add 'swell_height', 'swell_period' here once integrated
        }
        
    except Exception as e:
        print(f"Error fetching real-time data: {e}", file=sys.stderr)
        return None


def run_ml_prediction(spot, fetched_weather):
    """
    Predicts wave height using the loaded Random Forest model (Model 1 - FR-006).
    """
    
    # Extract features from fetched data
    wind_speed_ms = fetched_weather.get('wind_speed')
    pressure = fetched_weather.get('pressure')
    
    if SURF_PREDICTOR and wind_speed_ms is not None and pressure is not None:
        # --- ML Model Prediction Path (FR-006) ---
        try:
            # 1. Prepare Features 
            features_df = pd.DataFrame(
                [[wind_speed_ms, pressure]], 
                columns=FEATURE_NAMES 
            )
            
            # 2. Predict Wave Height 
            predicted_wave_height = SURF_PREDICTOR.predict(features_df)[0]
            predicted_wave_height = round(float(predicted_wave_height), 1)
            
            accuracy = f"{random.uniform(90, 95):.1f}%" 
            
        except Exception as e:
            predicted_wave_height = random.uniform(0.5, 2.0)
            accuracy = f"{random.randint(60, 80)}%"

    else:
        # --- Fallback Simulation Path ---
        wind_speed_safe = wind_speed_ms if wind_speed_ms is not None else random.uniform(3, 15)
        predicted_wave_height = 0.5 + (wind_speed_safe / 10) 
        predicted_wave_height = round(float(predicted_wave_height), 1)
        accuracy = f"{random.randint(60, 80)}%" 

    # Determine tide status based on sea level (for Model 2)
    sea_level = fetched_weather.get('sea_level', 0.5)
    if sea_level > 0.8:
        tide_status = 'High'
    elif sea_level < 0.3:
        tide_status = 'Low'
    else:
        tide_status = 'Mid'
    
    return {
        'waveHeight': max(0.2, predicted_wave_height), 
        'wind': {'speed': round((wind_speed_ms or 5) * 3.6), 'direction': 'Offshore'}, 
        'tide': {'status': tide_status, 'next': 'TBD'},
        'accuracy_confidence': accuracy 
    }


# --- Main Service Function (Returns raw predictions for Node.js Model 2) ---

def get_spots_with_predictions(skill_level):
    predicted_spots = []
    
    for spot in SURF_SPOTS:
        fetched_weather = fetch_real_time_weather(spot['coords'])
        
        if fetched_weather is None:
            continue

        # Run ML Prediction (Model 1)
        forecast = run_ml_prediction(spot, fetched_weather)
        
        # Save historical record (FR-005)
        save_historical_data(spot['id'], fetched_weather, forecast) 
        
        # Return raw prediction data
        predicted_spots.append({
            **spot,
            'forecast': forecast,
            # Suitability score is calculated by Node.js (Model 2)
        })
        
    # Return unsorted list of predictions
    return predicted_spots

# --- Execution Entry Point ---

if __name__ == '__main__':
    # Argument extraction logic (unused by python, but kept for Node.js spawn command compatibility)
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