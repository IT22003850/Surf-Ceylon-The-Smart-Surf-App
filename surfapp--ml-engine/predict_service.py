import sys
import os
import json
import joblib
import pandas as pd
import requests
import arrow
import random
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
STORMGLASS_API_KEY = os.getenv("STORMGLASS_API_KEY")
MODEL_FILENAME = 'surf_forecast_model.joblib'
MODEL_PATH = os.path.join(os.path.dirname(__file__), MODEL_FILENAME)

# --- Definitions (MUST MATCH train_model.py) ---
FEATURE_NAMES = [
    'swellHeight', 'swellPeriod', 'swellDirection', 'windSpeed',
    'windDirection', 'seaLevel', 'gust', 'secondarySwellHeight',
    'secondarySwellPeriod', 'secondarySwellDirection'
]
TARGET_NAMES = ['waveHeight', 'wavePeriod', 'windSpeed', 'windDirection']

# --- THIS IS THE FIX: 'coords' is now a simple flat array [lon, lat] ---
SURF_SPOTS = [
    {'id': '1', 'name': 'Arugam Bay', 'region': 'East Coast', 'coords': [81.829, 6.843]},
    {'id': '2', 'name': 'Weligama', 'region': 'South Coast', 'coords': [80.426, 5.972]},
    {'id': '3', 'name': 'Midigama', 'region': 'South Coast', 'coords': [80.383, 5.961]},
    {'id': '4', 'name': 'Hiriketiya', 'region': 'South Coast', 'coords': [80.686, 5.976]},
    {'id': '5', 'name': 'Okanda', 'region': 'East Coast', 'coords': [81.657, 6.660]},
]

# --- Model Loading ---
try:
    SURF_PREDICTOR = joblib.load(MODEL_PATH)
    print("Multi-output Random Forest Model loaded successfully.", file=sys.stderr)
except FileNotFoundError:
    SURF_PREDICTOR = None
    print(f"Warning: Model file not found at '{MODEL_PATH}'. Service will run in simulation mode.", file=sys.stderr)
except Exception as e:
    SURF_PREDICTOR = None
    print(f"Error loading model: {e}. Running in simulation mode.", file=sys.stderr)

def _get_average_from_sources(source_dict):
    if not source_dict: return None
    valid_values = [v for v in source_dict.values() if isinstance(v, (int, float))]
    return sum(valid_values) / len(valid_values) if valid_values else None

def fetch_future_weather_features(coords):
    if not STORMGLASS_API_KEY:
        print("API key is missing.", file=sys.stderr)
        return None, False

    lon, lat = coords
    start_time = arrow.utcnow()
    end_time = start_time.shift(hours=+1)
    
    try:
        response = requests.get(
            'https://api.stormglass.io/v2/weather/point',
            params={ 'lat': lat, 'lng': lon, 'params': ','.join(FEATURE_NAMES), 'start': start_time.timestamp(), 'end': end_time.timestamp() },
            headers={'Authorization': STORMGLASS_API_KEY}
        )
        response.raise_for_status()
        data = response.json()
        
        if not data.get('hours'): return None, False

        current_hour_data = data['hours'][0]
        features = {}
        is_data_valid = True
        for param in FEATURE_NAMES:
            value = _get_average_from_sources(current_hour_data.get(param, {}))
            if value is None:
                is_data_valid = False
            features[param] = value
        
        return features, is_data_valid
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}. Will use mock data.", file=sys.stderr)
        return None, False
    except Exception as e:
        print(f"Error processing weather data: {e}", file=sys.stderr)
        return None, False

def run_ml_prediction(features):
    input_df = pd.DataFrame([features], columns=FEATURE_NAMES)
    predictions_array = SURF_PREDICTOR.predict(input_df)
    predictions = dict(zip(TARGET_NAMES, predictions_array[0]))
    
    sea_level = features.get('seaLevel', 0.5)
    tide_status = 'High' if sea_level > 0.8 else ('Low' if sea_level < 0.3 else 'Mid')
    
    return {
        'waveHeight': round(float(predictions.get('waveHeight', 0)), 1),
        'wavePeriod': round(float(predictions.get('wavePeriod', 0)), 1),
        'windSpeed': round(float(predictions.get('windSpeed', 0)) * 3.6, 1),
        'windDirection': round(float(predictions.get('windDirection', 0)), 1),
        'tide': {'status': tide_status}
    }

def generate_mock_forecast(spot):
    print(f"Generating mock forecast for {spot['name']}.", file=sys.stderr)
    is_east_coast = spot['region'] == 'East Coast'
    
    return {
        'waveHeight': round(random.uniform(0.5, 2.2), 1),
        'wavePeriod': round(random.uniform(7, 14), 1),
        'windSpeed': round(random.uniform(5, 30), 1),
        'windDirection': round(random.uniform(250, 290) if is_east_coast else random.uniform(0, 50), 1),
        'tide': {'status': random.choice(['Low', 'Mid', 'High'])}
    }

def get_spots_with_predictions():
    all_spots_data = []
    for spot in SURF_SPOTS:
        features, is_valid = fetch_future_weather_features(spot['coords'])
        
        if SURF_PREDICTOR and is_valid:
            forecast = run_ml_prediction(features)
        else:
            forecast = generate_mock_forecast(spot)
        
        all_spots_data.append({**spot, 'forecast': forecast})
        
    return all_spots_data

if __name__ == '__main__':
    try:
        results = get_spots_with_predictions()
        print(json.dumps({'spots': results}))
    except Exception as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr)
        sys.exit(1)