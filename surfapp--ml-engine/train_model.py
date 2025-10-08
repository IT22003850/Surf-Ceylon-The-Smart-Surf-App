import pandas as pd
import numpy as np
import os
import joblib # For model serialization (saving/loading)
from dotenv import load_dotenv
from pymongo import MongoClient
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from datetime import datetime

# --- Configuration ---
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI") 
DB_NAME = 'surf_app_db'
COLLECTION_NAME = 'forecast_history'
MODEL_FILENAME = 'random_forest_surf_model.joblib'
MODEL_PATH = os.path.join(os.path.dirname(__file__), MODEL_FILENAME)

# --- 1. Data Retrieval and Feature Engineering (FR-006, FR-007) ---
def load_and_preprocess_data():
    """Simulates loading historical data and adding features."""
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        
        # In a real scenario, we'd load 24 months of data (FR-005)
        data_cursor = db[COLLECTION_NAME].find({}, {
            '_id': 0, 'raw_data': 1, 'prediction': 1, 'timestamp': 1, 'spot_id': 1
        })
        
        df = pd.DataFrame(list(data_cursor))
        
        if df.empty:
            print("No data found in MongoDB. Cannot train model.")
            return None

    except Exception as e:
        print(f"Error loading data from MongoDB: {e}")
        return None

    # --- Feature Engineering Simulation (FR-007: Tropical-specific factors) ---
    # For now, we simulate a simple dataset. In your final research,
    # you would create real features like:
    # df['monsoon_season'] = df['timestamp'].apply(lambda t: 1 if t.month in [5, 6, 7] else 0)
    
    # Since we only have mock data, we create a simple target feature (waveHeight)
    df['wave_height'] = df['prediction'].apply(lambda x: x['waveHeight'])
    df['wind_speed'] = df['raw_data'].apply(lambda x: x['wind_speed'])
    df['pressure'] = df['raw_data'].apply(lambda x: x['pressure'])
    
    # Define features (X) and target (y)
    X = df[['wind_speed', 'pressure']]
    y = df['wave_height']
    
    return X, y

# --- 2. Training the Random Forest Model (FR-006) ---
def train_model(X, y):
    """Trains the Random Forest Regressor."""
    print("Starting model training...")
    # Use RandomForestRegressor as specified in the proposal
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    # Split data for basic validation (not required for training, but good practice)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model.fit(X_train, y_train)
    
    # Evaluate model accuracy (FR-005: 95% accuracy target)
    accuracy = model.score(X_test, y_test)
    print(f"Model Training Complete. R-squared Score: {accuracy:.4f}")
    
    return model

# --- 3. Model Serialization ---
def save_model(model):
    """Saves the trained model to a file."""
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved successfully to {MODEL_PATH}")

if __name__ == '__main__':
    # Step 1: Load and Prepare Data
    data = load_and_preprocess_data()
    
    if data is not None:
        X, y = data
        
        # Step 2: Train Model
        trained_model = train_model(X, y)
        
        # Step 3: Save Model
        save_model(trained_model)
    else:
        print("Training aborted due to insufficient data.")