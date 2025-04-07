import pandas as pd
from pymongo import MongoClient
import os
import streamlit as st
import matplotlib.pyplot as plt


# Connect to MongoDB
client = MongoClient('mongo', 27017)


db = client['your_database']
collection_spotify = db['your_collection_spotify']
collection_rf = db['your_collection_rf']
collection_heat = db['your_collection_heat']
collection_rh = db['your_collection_rh']



# Fetch data from MongoDB
df_spotify_hk = pd.DataFrame(list(collection_spotify.find()))
df_hk_rf = pd.DataFrame(list(collection_rf.find()))
df_hk_heat = pd.DataFrame(list(collection_heat.find()))
df_hk_rh = pd.DataFrame(list(collection_rh.find()))



# Display data using Streamlit
st.title('Spotify HK')
st.write(df_spotify_hk)
st.title('RF')
st.write(df_hk_rf)
st.title('Heat')
st.write(df_hk_heat)
st.title('RH')
st.write(df_hk_rh)

    


