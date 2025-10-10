import arrow
import requests
import time
import json
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
STORMGLASS_API_KEY = os.getenv("STORMGLASS_API_KEY") 
MONGODB_URI = os.getenv("MONGODB_URI") 
DB_NAME = 'surf_app_db'
COLLECTION_NAME = 'historical_raw_data' # Dedicated collection for raw data dumps

# All 5 surf spots and their coordinates
SURF_SPOTS = [
    {'id': '1', 'name': 'Arugam Bay', 'lat': 6.843, 'lng': 81.829},
    {'id': '2', 'name': 'Weligama', 'lat': 5.972, 'lng': 80.426},
    {'id': '3', 'name': 'Midigama', 'lat': 5.961, 'lng': 80.383},
    {'id': '4', 'name': 'Hiriketiya', 'lat': 5.976, 'lng': 80.686},
    {'id': '5', 'name': 'Okanda', 'lat': 6.660, 'lng': 81.657},
]

# Features required for ML training, plus the target (waveHeight)
PARAMS = 'swellHeight,swellPeriod,waveHeight,windSpeed,seaLevel,airTemperature,pressure'
MAX_DAYS_PER_REQUEST = 10 # Stormglass historical limit

def connect_db():
    """Connects to MongoDB."""
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        return client.get_database(DB_NAME)
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}", file=sys.stderr)
        return None

def fetch_and_save_historical_data():
    """
    Fetches 10 days of historical data and saves to MongoDB (Initial FR-005).
    NOTE: For 24 months, the loop condition must be adjusted.
    """
    db = connect_db()
    if db is None:
        return

    # For the initial 10-day test:
    start_date = arrow.get('2023-10-01').to('utc')
    end_date = start_date.shift(days=+MAX_DAYS_PER_REQUEST)
    
    start_ts = start_date.timestamp()
    end_ts = end_date.timestamp()


    print(f"\n--- Starting 10-Day Historical Data Acquisition ---", file=sys.stderr)
    
    for spot in SURF_SPOTS:
        url = 'https://api.stormglass.io/v2/weather/point'
        
        try:
            response = requests.get(
                url,
                params={
                    'lat': spot['lat'],
                    'lng': spot['lng'],
                    'params': PARAMS,
                    'start': start_ts, 
                    'end': end_ts,
                },
                headers={'Authorization': STORMGLASS_API_KEY}
            )
            response.raise_for_status() 
            data = response.json()
            
            # --- Data Saving ---
            if 'hours' in data:
                records_to_insert = [
                    {'spot_id': spot['id'], 
                     'name': spot['name'],
                     'timestamp': r['time'], 
                     'raw_data': r}
                    for r in data['hours']
                ]
                db[COLLECTION_NAME].insert_many(records_to_insert)
                print(f"  Saved {len(records_to_insert)} records for {spot['name']}.", file=sys.stderr)
            
            time.sleep(2) 

        except requests.exceptions.RequestException as e:
            print(f"  API Error (HTTP {e.response.status_code}) for {spot['name']}: {e}", file=sys.stderr)
        
        except Exception as e:
            print(f"  General Error for {spot['name']}: {e}", file=sys.stderr)


if __name__ == '__main__':
    fetch_and_save_historical_data()