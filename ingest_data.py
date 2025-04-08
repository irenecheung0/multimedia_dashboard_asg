import pandas as pd
from pymongo import MongoClient
import os

# Load CSV files
try:
    df_spotify_hk = pd.read_csv(os.path.join('data', 'spotify_hk.csv'))
    df_hk_rf = pd.read_csv(os.path.join('data', '2021_daily_KP_RF.csv'))
    df_hk_heat = pd.read_csv(os.path.join('data', '2021_KP_MEANHKHI.csv'))
    df_hk_rh = pd.read_csv(os.path.join('data', '2021_daily_KP_RH.csv'))
except FileNotFoundError as e:
    print(f"CSV file not found: {e}")
    exit()

# Connect to MongoDB
try:
    client = MongoClient(os.getenv('MONGO_HOST', 'mongo'), int(os.getenv('MONGO_PORT', 27017)))
    db = client[os.getenv('MONGO_DB', 'your_database')]
    collection_spotify = db[os.getenv('MONGO_COLLECTION_SPOTIFY', 'your_collection_spotify')]
    collection_rf = db[os.getenv('MONGO_COLLECTION_RF', 'your_collection_rf')]
    collection_heat = db[os.getenv('MONGO_COLLECTION_HEAT', 'your_collection_heat')]
    collection_rh = db[os.getenv('MONGO_COLLECTION_RH', 'your_collection_rh')]
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit()

# Delete existing data in MongoDB collections
try:
    collection_spotify.delete_many({})
    collection_rf.delete_many({})
    collection_heat.delete_many({})
    collection_rh.delete_many({})
    print("Existing data deleted successfully.")
except Exception as e:
    print(f"Error deleting data from MongoDB: {e}")
    exit()

# Insert data into MongoDB
try:
    collection_spotify.insert_many(df_spotify_hk.to_dict('records'))
    collection_rf.insert_many(df_hk_rf.to_dict('records'))
    collection_heat.insert_many(df_hk_heat.to_dict('records'))
    collection_rh.insert_many(df_hk_rh.to_dict('records'))
    print("Data ingestion completed successfully.")
except Exception as e:
    print(f"Error inserting data into MongoDB: {e}")
