import pandas as pd
import numpy as np
import os
import joblib 
import arrow 
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from pymongo import MongoClient
import requests
import sys

# --- Configuration ---
load_dotenv()
STORMGLASS_API_KEY = os.getenv("STORMGLASS_API_KEY") 
MONGODB_URI = os.getenv("MONGODB_URI") 
MODEL_FILENAME = 'random_forest_surf_model.joblib'
MODEL_PATH = os.path.join(os.path.dirname(__file__), MODEL_FILENAME)

# Feature names used for training (CRITICAL: MUST MATCH predict_service.py)
FEATURE_NAMES = ['windSpeed', 'swellHeight', 'swellPeriod', 'seaLevel'] 

# Spot data (Using Weligama for the small training set)
SURF_SPOT = {'id': '2', 'name': 'Weligama', 'lat': 5.972, 'lng': 80.426}


# --- 1. Data Acquisition from Stormglass (Historical) ---

def fetch_historical_data_for_training():
    """Fetches 10 days of high-value marine historical data directly from Stormglass."""
    if not STORMGLASS_API_KEY:
        print("Error: STORMGLASS_API_KEY is missing.", file=sys.stderr)
        return None

    # Define 10-day historical window (2023-10-01 to 2023-10-11)
    # Using the fixed, validated UNIX timestamps for stability
    start_time = 1696118400  # 2023-10-01T00:00:00Z
    end_time = 1697079600    # 2023-10-11T00:00:00Z
    
    # All parameters required for the ML model (features) + the target (waveHeight)
    params = ','.join(FEATURE_NAMES + ['waveHeight', 'airTemperature', 'pressure']) 
    
    url = 'https://api.stormglass.io/v2/weather/point'
    
    try:
        response = requests.get(
            url,
            params={
                'lat': SURF_SPOT['lat'],
                'lng': SURF_SPOT['lng'],
                'params': params,
                'start': start_time,
                'end': end_time,
            },
            headers={'Authorization': STORMGLASS_API_KEY}
        )
        response.raise_for_status() 
        data = response.json()
        
        if 'hours' not in data or not data['hours']:
            print("Stormglass returned empty historical data set.", file=sys.stderr)
            return None

        print(f"Successfully fetched {len(data['hours'])} hourly records for training.", file=sys.stderr)
        
        # --- Preprocessing and Flattening Data ---
        processed_data = []
        for hourly_record in data['hours']:
            features = {}
            valid_record = True
            
            for param in FEATURE_NAMES + ['waveHeight']:
                # Extract the 'sg' (Stormglass) source value
                value = hourly_record.get(param, {}).get('sg') 
                if value is None:
                    # Mark record as invalid if a critical value is missing
                    valid_record = False 
                    break 
                features[param] = float(value)
            
            if valid_record:
                processed_data.append(features)

        # The DataFrame contains FEATURE_NAMES columns + 'waveHeight' (Target)
        return pd.DataFrame(processed_data)

    except requests.exceptions.RequestException as e:
        print(f"CRITICAL API ERROR: Failed to fetch historical data: {e}", file=sys.stderr)
        return None


# --- 2. Training the Random Forest Model (FR-006) ---
def train_model(df):
    """Trains Model 1 (Random Forest Regressor) on historical data."""
    print("Starting model training (Random Forest Regressor)...", file=sys.stderr)
    
    # Define features (X) and target (y)
    X = df[FEATURE_NAMES]
    y = df['waveHeight'] # Target is the combined wave height
    
    # Use a small test size since the dataset is only 10 days long
    # Use the full dataset for max learning since it's just a demo training
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)
    
    # Evaluate model accuracy (simple self-score)
    accuracy = model.score(X, y)
    print(f"Model Training Complete. R-squared Score: {accuracy:.4f}", file=sys.stderr)
    
    # Save the model
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved successfully to {MODEL_PATH}", file=sys.stderr)


if __name__ == '__main__':
    try:
        # Step 1: Fetch and Prepare Data
        training_df = fetch_historical_data_for_training()
        
        if training_df is not None and not training_df.empty:
            # Step 2: Train Model
            train_model(training_df)
        else:
            print("Training aborted: No valid historical data to train the model.", file=sys.stderr)

    except Exception as e:
        print(f"CRITICAL TRAINING ERROR: {e}", file=sys.stderr)