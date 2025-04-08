import pandas as pd
from pymongo import MongoClient
import os
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np


#st.title("COMP7503 Multimedia Technologies Project")

intro = st.Page("1_introduction.py", title="Introduction", icon="🏠")
spotify_eda = st.Page("2_spotify_eda.py", title="Spotify Chart Data EDA", icon="🎷")
weather_eda = st.Page("3_weather_eda.py", title="Weather Data EDA", icon="🌤️")
correlation = st.Page("4_correlation.py", title="Correlation", icon="📈")
playlist = st.Page("5_spotify_playlist.py", title="Generate Spotify Playlist", icon="💿")

pg = st.navigation([intro, spotify_eda, weather_eda, correlation, playlist])
pg.run()


# Define functions before using them
def get_value_mean_of_years(df, years):
    df = df[df['Year'].isin(years)]
    mean_value = df['Value'].mean()
    max_value = df['Value'].max()
    min_value = df['Value'].min()
    return mean_value, max_value, min_value


def normalize_value(x, average_value, min_value, max_value):
    if x <= average_value:
        return 0.5 * (x - min_value) / (average_value - min_value)
    else:
        return 0.5 + 0.5 * (x - average_value) / (max_value - average_value)


def calculate_normalized_value(df):
    df = df.copy()
    
    mean_value, max_value, min_value = get_value_mean_of_years(df, ['2021', '2022'])
    
    # Create piecewise linear mapping
    df['normalizedValue'] = df['Value'].apply(
        lambda x: 0.5 * (x - min_value) / (mean_value - min_value) if x <= mean_value 
        else 0.5 + 0.5 * (x - mean_value) / (max_value - mean_value)
    )
    
    # Clip values to ensure they stay within [0,1]
    df['normalizedValue'] = df['normalizedValue'].clip(0, 1)
    
    return df


def clean_weather_data(df):
    # Create a copy of the DataFrame to avoid SettingWithCopyWarning
    df = df.copy()
    
    # Convert Year to string first
    df['Year'] = df['Year'].astype(str)
    
    # remove records with invalid year
    df = df[df['Year'].str.match(r'^\d{4}$')].copy()
    df['Year'] = df['Year'].astype(str)
    df['Month'] = df['Month'].fillna(0).astype(int).astype(str).str.zfill(2)
    df['Day'] = df['Day'].fillna(0).astype(int).astype(str).str.zfill(2)
    df['date'] = pd.to_datetime(df['Year'] + '-' + df['Month'] + '-' + df['Day'], format='%Y-%m-%d')
    df['WeekNumber'] = df['date'].dt.isocalendar().week
    df['YW'] = df['Year'] + '-' + df['WeekNumber'].astype(str).str.zfill(2)
    
    # Handle '***' values in Value column
    df['Value'] = df['Value'].replace('***', np.nan)
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    df = df[df['Value'].notna()].copy()
    df = calculate_normalized_value(df)
    
    print(f"Year: {df['Year'].unique()}")
    print(f"Month: {df['Month'].unique()}")
    print(f"Day: {df['Day'].unique()}")
    print(f"WeekNumber: {df['YW'].min()} - {df['YW'].max()}")
    return df


def merge_weather_spotify():
    # Calculate average weekly metrics for each weather feature
    weekly_heat = df_hk_heat.groupby('YW')['normalizedValue'].mean().reset_index()
    weekly_heat.columns = ['report_date_YW', 'avg_heat']

    weekly_rain = df_hk_rf.groupby('YW')['normalizedValue'].mean().reset_index()
    weekly_rain.columns = ['report_date_YW', 'avg_rainfall']

    weekly_humidity = df_hk_rh.groupby('YW')['normalizedValue'].mean().reset_index()
    weekly_humidity.columns = ['report_date_YW', 'avg_humidity']
    
    weather_spotify = df_spotify_hk.merge(weekly_heat, on='report_date_YW', how='inner')
    weather_spotify = weather_spotify.merge(weekly_rain, on='report_date_YW', how='inner')
    weather_spotify = weather_spotify.merge(weekly_humidity, on='report_date_YW', how='inner')
    
    return weather_spotify


def remove_duplicates_by_week_and_uri(df):
    """
    Remove duplicate records with the same report_date_YW and uri
    
    Args:
        df: DataFrame containing 'report_date_YW' and 'uri' columns
        
    Returns:
        DataFrame with duplicates removed
    """
    # Count total records before deduplication
    initial_count = len(df)
    
    # Drop duplicates based on report_date_YW and uri
    df_deduplicated = df.drop_duplicates(subset=['report_date_YW', 'uri'], keep='first')
    
    # Count total records after deduplication
    final_count = len(df_deduplicated)
    
    # Calculate number of duplicates removed
    duplicates_removed = initial_count - final_count
    
    # Display info about deduplication process
    if duplicates_removed > 0:
        st.info(f"Removed {duplicates_removed} duplicate records from the dataset. Original: {initial_count}, After deduplication: {final_count}")
    
    return df_deduplicated



client = MongoClient('mongo', 27017)
db = client['your_database']


## Load data from MongoDB
if 'data_spotify_hk' not in st.session_state:
    collection_spotify = db['your_collection_spotify']
    df_spotify_hk = pd.DataFrame(list(collection_spotify.find()))
    df_spotify_hk = remove_duplicates_by_week_and_uri(df_spotify_hk)
    st.session_state['data_spotify_hk'] = df_spotify_hk

if 'data_weather_hk_rf' not in st.session_state:
    collection_rf = db['your_collection_rf']
    df_hk_rf = pd.DataFrame(list(collection_rf.find()))
    df_hk_rf = clean_weather_data(df_hk_rf)
    st.session_state['data_weather_hk_rf'] = df_hk_rf
    
if 'data_weather_hk_heat' not in st.session_state:
    collection_heat = db['your_collection_heat']
    df_hk_heat = pd.DataFrame(list(collection_heat.find()))
    df_hk_heat = clean_weather_data(df_hk_heat)
    st.session_state['data_weather_hk_heat'] = df_hk_heat
    
if 'data_weather_hk_rh' not in st.session_state:
    collection_rh = db['your_collection_rh']
    df_hk_rh = pd.DataFrame(list(collection_rh.find()))
    df_hk_rh = clean_weather_data(df_hk_rh)
    st.session_state['data_weather_hk_rh'] = df_hk_rh

if 'data_weather_spotify' not in st.session_state:
    df_weather_spotify = merge_weather_spotify()
    st.session_state['data_weather_spotify'] = df_weather_spotify

