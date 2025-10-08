import json
import sys
import random
from datetime import datetime
from math import sin
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import requests

# --- Setup and Constants ---

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI") 

# Static spot data (Will eventually be loaded from DB)
SURF_SPOTS = [
    {'id': '1', 'name': 'Arugam Bay', 'region': 'East Coast', 'coords': [81.829, 6.843], 'city_name': 'Ampara'},
    {'id': '2', 'name': 'Weligama', 'region': 'South Coast', 'coords': [80.426, 5.972], 'city_name': 'Weligama'},
    {'id': '3', 'name': 'Midigama', 'region': 'South Coast', 'coords': [80.383, 5.961], 'city_name': 'Weligama'}, 
    {'id': '4', 'name': 'Hiriketiya', 'region': 'South Coast', 'coords': [80.686, 5.976], 'city_name': 'Dikwella'}, 
    {'id': '5', 'name': 'Okanda', 'region': 'East Coast', 'coords': [81.657, 6.660], 'city_name': 'Pottuvil'},
]

# --- DATABASE FUNCTIONS (FR-005) ---

def connect_to_mongodb():
    """Establishes connection to the MongoDB Atlas cluster and returns the database object."""
    if not MONGODB_URI:
        print("Error: MONGODB_URI is missing. Cannot connect to database.", file=sys.stderr)
        return None
    try:
        # Connect to the client. This part usually succeeds quickly.
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        
        # The connection attempt is deferred until the first operation (e.g., client.admin.command('ping'))
        client.admin.command('ping') 
        
        # Successfully connected, return the database instance
        return client.get_database('surf_app_db')
        
    except Exception as e:
        # Log the detailed failure (e.g., DNS error, authentication failure, timeout)
        print(f"Error connecting to MongoDB: {e}", file=sys.stderr)
        return None

def save_historical_data(spot_id, raw_data, prediction):
    """Saves a snapshot of raw API data and the resulting prediction to MongoDB."""
    db = connect_to_mongodb()
    
    # CRITICAL FIX: Check explicitly for None, as recommended by PyMongo
    if db is not None: 
        try:
            history_collection = db['forecast_history']
            record = {
                'spot_id': spot_id,
                'timestamp': datetime.utcnow(),
                'raw_data': raw_data,
                'prediction': prediction
            }
            # Insert operation
            history_collection.insert_one(record)
        except Exception as e:
            # Log failure to insert record if connection fails post-check (less common)
            print(f"Error inserting record into MongoDB: {e}", file=sys.stderr)
    else:
        # If the connection failed, log a warning and proceed (Graceful Degradation - NFR-012)
        print("Warning: Skipping database save due to connection failure.", file=sys.stderr)


# --- API FETCH & ML Simulation ---

def fetch_real_time_weather(city_name):
    """Fetches real-time wind/weather data from OpenWeather API."""
    if not OPENWEATHER_API_KEY:
        print("Error: OPENWEATHER_API_KEY is missing. Check .env file.", file=sys.stderr)
        return None

    # OpenWeather API URL using city name for simplicity
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name},LK&appid={OPENWEATHER_API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        response.raise_for_status() 
        data = response.json()
        
        # Data Cleaning/Extraction
        return {
            'timestamp': datetime.now().isoformat(),
            'wind_speed': data['wind']['speed'], # m/s
            'pressure': data['main']['pressure'],
            'temp': data['main']['temp'],
        }
    except requests.exceptions.RequestException as e:
        # Log HTTP/Network errors
        print(f"Error fetching OpenWeather for {city_name}: {e}", file=sys.stderr)
        return None


def run_ml_prediction(spot, fetched_weather):
    """
    Simulates ML prediction using fetched wind data.
    (This function will be replaced with actual Random Forest logic later)
    """
    
    # Use fetched wind speed, defaulting to a random value if API failed
    wind_speed_ms = fetched_weather.get('wind_speed', random.randint(3, 15))
    
    # Mock wave height calculation incorporating wind influence
    seed = datetime.now().hour + int(spot['id'])
    random.seed(seed)
    wave_height = round(0.5 + (wind_speed_ms / 10) + random.uniform(-0.3, 0.3), 1)
    wave_height = max(0.5, wave_height)
    
    # Mock tide status
    tide_status = 'High' if sin(datetime.now().hour * 0.5 + int(spot['id'])) > 0 else 'Low'
    
    return {
        'waveHeight': float(wave_height),
        # Convert m/s to kph for frontend display (1 m/s = 3.6 kph)
        'wind': {'speed': round(wind_speed_ms * 3.6), 'direction': 'Offshore'}, 
        'tide': {'status': tide_status, 'next': 'TBD'},
        'accuracy_confidence': f"{random.randint(85, 95)}%" # FR-009 Placeholder
    }


def calculate_suitability(forecast, skill_level):
    """Applies the core recommendation logic (FR-011)."""
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


# --- Main Service Function ---

def get_spots_with_predictions(skill_level):
    predicted_spots = []
    
    for spot in SURF_SPOTS:
        # Step 1: Fetch Real-Time Data (FR-002)
        fetched_weather = fetch_real_time_weather(spot['city_name'])
        
        if fetched_weather is None:
            # If API fails, skip this spot for this iteration
            continue

        # Step 2: Run ML Prediction on Fetched Data (FR-006)
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