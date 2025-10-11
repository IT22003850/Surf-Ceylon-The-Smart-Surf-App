import pandas as pd
import joblib
import os
import requests
import sys
import arrow
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# --- Configuration ---
load_dotenv()
STORMGLASS_API_KEY = os.getenv("STORMGLASS_API_KEY")
MODEL_FILENAME = 'surf_forecast_model.joblib' # New model name for the multi-output model
MODEL_PATH = os.path.join(os.path.dirname(__file__), MODEL_FILENAME)

# --- Features & Targets Definition ---
# These are the inputs the model will learn from.
FEATURE_NAMES = [
    'swellHeight', 'swellPeriod', 'swellDirection', 'windSpeed',
    'windDirection', 'seaLevel', 'gust', 'secondarySwellHeight',
    'secondarySwellPeriod', 'secondarySwellDirection'
]
# These are the multiple outputs the model will predict.
TARGET_NAMES = ['waveHeight', 'wavePeriod', 'windSpeed', 'windDirection']

# A single spot is used for this focused training example.
SURF_SPOT = {'id': '2', 'name': 'Weligama', 'lat': 5.972, 'lng': 80.426}
MAX_DAYS_PER_REQUEST = 10 # Stormglass historical data limit

def _get_average_from_sources(source_dict):
    """
    Averages the values from different weather sources (e.g., sg, noaa, meteo).
    This creates a more robust single value for each parameter.
    """
    if not source_dict: return None
    valid_values = [v for v in source_dict.values() if isinstance(v, (int, float))]
    return sum(valid_values) / len(valid_values) if valid_values else None

def fetch_historical_data_for_training():
    """Fetches and processes historical data for both features and targets."""
    if not STORMGLASS_API_KEY:
        print("Error: STORMGLASS_API_KEY environment variable is not set.", file=sys.stderr)
        return None

    # Fetch the last 10 days of data for training.
    start_date = arrow.utcnow().shift(days=-MAX_DAYS_PER_REQUEST)
    end_date = arrow.utcnow()
    
    # Request all parameters needed for both the features and the targets.
    all_params = ','.join(list(set(FEATURE_NAMES + TARGET_NAMES)))
    
    try:
        response = requests.get(
            'https://api.stormglass.io/v2/weather/point',
            params={
                'lat': SURF_SPOT['lat'], 
                'lng': SURF_SPOT['lng'],
                'params': all_params,
                'start': start_date.timestamp(), 
                'end': end_date.timestamp(),
            },
            headers={'Authorization': STORMGLASS_API_KEY}
        )
        response.raise_for_status()
        data = response.json()
        
        if 'hours' not in data or not data['hours']:
            print("Warning: Stormglass API returned no historical data.", file=sys.stderr)
            return None

        print(f"Successfully fetched {len(data['hours'])} hourly records for training.", file=sys.stderr)
        
        # Process the raw hourly data into a clean list of records
        processed_data = []
        for hour in data['hours']:
            record = {}
            is_valid_record = True
            for param in all_params.split(','):
                value = _get_average_from_sources(hour.get(param, {}))
                if value is None:
                    is_valid_record = False
                    break
                record[param] = value
            if is_valid_record:
                processed_data.append(record)

        return pd.DataFrame(processed_data)

    except requests.exceptions.RequestException as e:
        print(f"CRITICAL API ERROR: Could not fetch training data from Stormglass. {e}", file=sys.stderr)
        return None

def train_model(df):
    """Trains a multi-output Random Forest Regressor and saves it to a file."""
    if df.empty:
        print("Training cannot proceed with an empty DataFrame.", file=sys.stderr)
        return

    print("Starting multi-output model training (Random Forest Regressor)...", file=sys.stderr)
    
    # Define the features (X) and the multiple targets (y)
    X = df[FEATURE_NAMES]
    y = df[TARGET_NAMES]
    
    # Split data for training and testing
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Initialize and train the model
    # n_jobs=-1 uses all available CPU cores for faster training
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # Evaluate the model's performance on the test set
    accuracy = model.score(X_test, y_test)
    print(f"Model Training Complete. R-squared Score on test data: {accuracy:.4f}", file=sys.stderr)
    
    # Save the trained model to disk
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved successfully to '{MODEL_PATH}'", file=sys.stderr)

if __name__ == '__main__':
    # Step 1: Fetch and Prepare Data
    training_df = fetch_historical_data_for_training()
    
    # Step 2: Train Model if data is valid
    if training_df is not None and not training_df.empty:
        train_model(training_df)
    else:
        print("Training aborted due to lack of valid historical data.", file=sys.stderr)