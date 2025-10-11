import sys
import os
import json
import joblib
import pandas as pd
import requests
import arrow
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
STORMGLASS_API_KEY = os.getenv("STORMGLASS_API_KEY")
MODEL_FILENAME = 'surf_forecast_model.joblib' # Correct model file
MODEL_PATH = os.path.join(os.path.dirname(__file__), MODEL_FILENAME)

# --- 🎯 Definitions (MUST MATCH train_model.py) ---
FEATURE_NAMES = [
    'swellHeight', 'swellPeriod', 'swellDirection', 'windSpeed',
    'windDirection', 'seaLevel', 'gust', 'secondarySwellHeight',
    'secondarySwellPeriod', 'secondarySwellDirection'
]
TARGET_NAMES = ['waveHeight', 'wavePeriod', 'windSpeed', 'windDirection']

# Static data for all surf spots
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
    print(f"Warning: Model file not found at '{MODEL_PATH}'. The service will run in simulation mode.", file=sys.stderr)
except Exception as e:
    SURF_PREDICTOR = None
    print(f"Error loading model: {e}. Running in simulation mode.", file=sys.stderr)

def _get_average_from_sources(source_dict):
    """Averages values from different weather sources."""
    if not source_dict: return None
    valid_values = [v for v in source_dict.values() if isinstance(v, (int, float))]
    return sum(valid_values) / len(valid_values) if valid_values else None

def fetch_future_weather_features(coords):
    """Fetches future weather data needed for Model 1's input features."""
    if not STORMGLASS_API_KEY:
        return None, False

    lon, lat = coords
    start_time = arrow.utcnow()
    end_time = start_time.shift(hours=+1) # Fetch data for the current hour
    
    try:
        response = requests.get(
            'https://api.stormglass.io/v2/weather/point',
            params={
                'lat': lat, 'lng': lon,
                'params': ','.join(FEATURE_NAMES),
                'start': start_time.timestamp(), 'end': end_time.timestamp(),
            },
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
                is_data_valid = False # Mark as invalid if a feature is missing
            features[param] = value
        
        return features, is_data_valid
    except Exception as e:
        print(f"Error fetching real-time weather: {e}", file=sys.stderr)
        return None, False

def run_ml_prediction(features):
    """
    Uses the loaded multi-output model to predict a full set of surf conditions.
    """
    # Create a DataFrame with the correct feature names
    input_df = pd.DataFrame([features], columns=FEATURE_NAMES)
    
    # The model predicts all targets at once, returning an array like [[val1, val2, ...]]
    predictions_array = SURF_PREDICTOR.predict(input_df)
    
    # Map the predicted values back to their names
    predictions = dict(zip(TARGET_NAMES, predictions_array[0]))
    
    # --- Post-process and format the final forecast object ---
    # Determine tide status based on the seaLevel feature
    sea_level = features.get('seaLevel', 0.5)
    tide_status = 'High' if sea_level > 0.8 else ('Low' if sea_level < 0.3 else 'Mid')
    
    return {
        'waveHeight': round(float(predictions.get('waveHeight', 0)), 1),
        'wavePeriod': round(float(predictions.get('wavePeriod', 0)), 1),
        'windSpeed': round(float(predictions.get('windSpeed', 0)) * 3.6, 1), # Convert m/s to kph
        'windDirection': round(float(predictions.get('windDirection', 0)), 1),
        'tide': {'status': tide_status}
    }

def get_spots_with_predictions():
    """Main function to iterate through spots, fetch features, and get predictions."""
    all_spots_data = []
    for spot in SURF_SPOTS:
        features, is_valid = fetch_future_weather_features(spot['coords'])
        
        if SURF_PREDICTOR and is_valid:
            # If model is loaded and data is valid, run ML prediction
            forecast = run_ml_prediction(features)
        else:
            # Fallback simulation if model or data is unavailable
            forecast = {
                'waveHeight': round(features.get('swellHeight', 1.0) * 1.2, 1) if features else 1.2,
                'wavePeriod': 8, 'windSpeed': 15, 'windDirection': 270,
                'tide': {'status': 'Mid'}
            }
        
        all_spots_data.append({**spot, 'forecast': forecast})
        
    return all_spots_data

if __name__ == '__main__':
    try:
        # The script now runs independently of user input and returns all spots
        results = get_spots_with_predictions()
        # The final output is a JSON string printed to standard output
        print(json.dumps({'spots': results}))
    except Exception as e:
        # Print errors to stderr so Node.js can capture them
        print(json.dumps({'error': str(e)}), file=sys.stderr)
        sys.exit(1)