import json
import sys
import random
from datetime import datetime
from math import sin, cos, pi
import os
from dotenv import load_dotenv
from pymongo import MongoClient # NEW IMPORT: MongoDB client

# --- Setup and Constants ---

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI") # NEW: Get MongoDB URI

# Static spot data (Will eventually be loaded from DB)
SURF_SPOTS = [
    {'id': '1', 'name': 'Arugam Bay', 'region': 'East Coast', 'coords': [81.829, 6.843], 'city_name': 'Ampara'},
    {'id': '2', 'name': 'Weligama', 'region': 'South Coast', 'coords': [80.426, 5.972], 'city_name': 'Weligama'},
    {'id': '3', 'name': 'Midigama', 'region': 'South Coast', 'coords': [80.383, 5.961], 'city_name': 'Weligama'}, # Using Weligama city for mock API
    {'id': '4', 'name': 'Hiriketiya', 'region': 'South Coast', 'coords': [80.686, 5.976], 'city_name': 'Dikwella'}, # Using Dikwella city for mock API
    {'id': '5', 'name': 'Okanda', 'region': 'East Coast', 'coords': [81.657, 6.660], 'city_name': 'Pottuvil'}, # Using Pottuvil city for mock API
]

# --- NEW: DATABASE FUNCTIONS (FR-005) ---

def connect_to_mongodb():
    """Establishes connection to the MongoDB Atlas cluster."""
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI is missing. Cannot connect to database.")
    try:
        client = MongoClient(MONGODB_URI)
        # Ping the server to verify connection
        client.admin.command('ping') 
        db = client.get_database('surf_app_db')
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}", file=sys.stderr)
        return None

def save_historical_data(spot_id, raw_data, prediction):
    """Saves a snapshot of raw API data and the resulting prediction."""
    db = connect_to_mongodb()
    if db:
        history_collection = db['forecast_history']
        record = {
            'spot_id': spot_id,
            'timestamp': datetime.utcnow(),
            'raw_data': raw_data,
            'prediction': prediction
        }
        # In a real system, we'd ensure data integrity here (FR-004)
        history_collection.insert_one(record)
        
# --- ML Prediction (Updated to call save_historical_data) ---

def fetch_real_time_weather(city_name):
    # ... (Keep the existing API fetching code from last step)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name},LK&appid={OPENWEATHER_API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'wind_speed': data['wind']['speed'], # m/s
            'pressure': data['main']['pressure'],
            'temp': data['main']['temp'],
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching OpenWeather for {city_name}: {e}", file=sys.stderr)
        return None


def run_ml_prediction(spot, fetched_weather):
    # ... (Keep the existing ML simulation logic, using wind_speed_ms)
    wind_speed_ms = fetched_weather.get('wind_speed', random.randint(3, 15))
    
    seed = datetime.now().hour + int(spot['id'])
    random.seed(seed)
    wave_height = round(0.5 + (wind_speed_ms / 10) + random.uniform(-0.3, 0.3), 1)
    wave_height = max(0.5, wave_height)
    
    tide_status = 'High' if sin(datetime.now().hour * 0.5 + int(spot['id'])) > 0 else 'Low'
    
    return {
        'waveHeight': float(wave_height),
        'wind': {'speed': round(wind_speed_ms * 3.6), 'direction': 'Offshore'}, 
        'tide': {'status': tide_status, 'next': 'TBD'},
        'accuracy_confidence': f"{random.randint(85, 95)}%"
    }

# --- Main Service Function (Updated to save data) ---

def get_spots_with_predictions(skill_level):
    predicted_spots = []
    
    for spot in SURF_SPOTS:
        fetched_weather = fetch_real_time_weather(spot['city_name'])
        
        if fetched_weather is None:
            continue

        forecast = run_ml_prediction(spot, fetched_weather)
        suitability = calculate_suitability(forecast, skill_level)
        
        # NEW: Save the historical record (FR-005)
        # We save the raw weather data and the result of the prediction
        save_historical_data(spot['id'], fetched_weather, forecast) 
        
        predicted_spots.append({
            **spot,
            'forecast': forecast,
            'suitability': suitability
        })
        
    predicted_spots.sort(key=lambda x: x['suitability'], reverse=True)
    return predicted_spots


# --- Execution Entry Point ---
# ... (Keep the existing __main__ block)
def calculate_suitability(forecast, skill_level):
    # ... (Keep the existing implementation)
    score = 100
    wave_height = forecast['waveHeight']

    if skill_level == 'Beginner':
        if wave_height > 1.5: score -= 60
        elif wave_height > 1.0: score -= 30
    elif skill_level == 'Intermediate':
        if wave_height < 1.0: score -= 20
        if wave_height > 2.5: score -= 40
    elif skill_level == 'Advanced':
        if wave_height < 1.8: score -= 30

    return max(0, min(100, score))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        skill = sys.argv[1]
    else:
        skill = 'Beginner' 

    try:
        # Before running predictions, ensure MongoDB connection works
        db_connection_test = connect_to_mongodb()
        if not db_connection_test:
            raise ConnectionError("Failed to establish necessary database connection.")
        
        results = get_spots_with_predictions(skill)
        print(json.dumps({'spots': results}))
        
    except Exception as e:
        sys.stderr.write(json.dumps({'error': str(e), 'traceback': str(e)}))
        sys.exit(1)