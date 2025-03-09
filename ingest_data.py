import pandas as pd
from pymongo import MongoClient

# Load CSV file
df = pd.read_csv('/data/netflix_users.csv')

# Connect to MongoDB
client = MongoClient('mongo', 27017)
db = client['your_database']
collection = db['your_collection']

# Insert data into MongoDB
collection.insert_many(df.to_dict('records'))


# Print a message indicating completion
print("Data ingestion completed successfully.")