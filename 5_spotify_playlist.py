import streamlit as st
import pandas as pd
import requests
import datetime


# Load custom CSS
def load_css():
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Apply custom CSS
load_css()


if ('data_weather_spotify' in st.session_state) and \
    ('data_spotify_hk' in st.session_state) and \
    ('data_weather_hk_rf' in st.session_state) and \
    ('data_weather_hk_heat' in st.session_state) and \
    ('data_weather_hk_rh' in st.session_state):
    df_weather_spotify = st.session_state['data_weather_spotify']
    df_spotify_hk = st.session_state['data_spotify_hk']
    df_hk_rf = st.session_state['data_weather_hk_rf']
    df_hk_heat = st.session_state['data_weather_hk_heat']
    df_hk_rh = st.session_state['data_weather_hk_rh']
else:
    st.switch_page("1_introduction.py")
    
def get_weather_data():
    # API URL
    url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=en"
    
    try:
        # Make the API request
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse JSON response
        data = response.json()
        
        # Extract required values
        current_rainfall = next((item['max'] for item in data['rainfall']['data'] if item['place'] == "Yau Tsim Mong"), None)
        current_tmp = next((item['value'] for item in data['temperature']['data'] if item['place'] == "King's Park"), None)
        current_humidity = next((item['value'] for item in data['humidity']['data'] if item['place'] == "Hong Kong Observatory"), None)
        
        # Return the extracted values
        return {
            "current_rainfall": current_rainfall,
            "current_tmp": current_tmp,
            "current_humidity": current_humidity
        }
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None


def normalize_value(x, average_value, min_value, max_value):
    if x <= average_value:
        return 0.5 * (x - min_value) / (average_value - min_value)
    else:
        return 0.5 + 0.5 * (x - average_value) / (max_value - average_value)


def get_value_mean_of_years(df, years):
    df = df[df['Year'].isin(years)]
    mean_value = df['Value'].mean()
    max_value = df['Value'].max()
    min_value = df['Value'].min()
    return mean_value, max_value, min_value


def calculate_and_get_top_20(df, target_heat, target_rainfall, target_humidity):
    """
    Calculate a score based on the difference between target values and averages,
    and return the top 20 rows with the smallest scores.
    
    Parameters:
        df (pd.DataFrame): The input DataFrame containing avg_heat, avg_rainfall, and avg_humidity columns.
        target_heat (float): The target heat value.
        target_rainfall (float): The target rainfall value.
        target_humidity (float): The target humidity value.
    
    Returns:
        pd.DataFrame: Top 20 rows sorted by the smallest scores.
    """
    # Calculate the score based on absolute differences
    df['score'] = (
        abs(df['avg_heat'] - target_heat) +
        abs(df['avg_rainfall'] - target_rainfall) +
        abs(df['avg_humidity'] - target_humidity)
    )
    
     # Sort by score and keep only the first occurrence of each URI (the one with smallest score)
    unique_tracks = df.sort_values('score').drop_duplicates('uri', keep='first')
    
    # Get the top 20 unique tracks with the smallest scores
    top_20 = unique_tracks.nsmallest(20, 'score')
    
    return top_20


# Example usage
weather_info = get_weather_data()
hk_tmp_mean, hk_tmp_max, hk_tmp_min = get_value_mean_of_years(df_hk_heat, ['2021','2022'])
#st.write(hk_tmp_mean, hk_tmp_max, hk_tmp_min)

hk_rf_mean, hk_rf_max, hk_rf_min = get_value_mean_of_years(df_hk_rf, ['2021','2022'])
#st.write(hk_rf_mean, hk_rf_max, hk_rf_min)

hk_rh_mean, hk_rh_max, hk_rh_min = get_value_mean_of_years(df_hk_rh, ['2021','2022'])
#st.write(hk_rh_mean, hk_rh_max, hk_rh_min)

target_heat = normalize_value(weather_info['current_tmp'], hk_tmp_mean, hk_tmp_min, hk_tmp_max)
target_rainfall = normalize_value(weather_info['current_rainfall'], hk_rf_mean, hk_rf_min, hk_rf_max)
target_humidity = normalize_value(weather_info['current_humidity'], hk_rh_mean, hk_rh_min, hk_rh_max)

#st.write(target_heat, target_rainfall, target_humidity)

top20 = calculate_and_get_top_20(df_weather_spotify, target_heat, target_rainfall, target_humidity)
#st.write(top20)

# Display weather information
st.header("Current Weather Conditions")

# Add today's date
today = datetime.datetime.now().strftime("%A, %B %d, %Y")
st.subheader(f"{today}")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Temperature 🌡️", f"{weather_info['current_tmp']}°C")
with col2:
    st.metric("Rainfall 🌧️", f"{weather_info['current_rainfall']} mm")
with col3:
    st.metric("Humidity 💦", f"{weather_info['current_humidity']}%")

# Display the playlist
st.header("Your Weather-Based Playlist")
#st.write("Songs that match the current weather conditions")

# Function to format duration from ms to mm:ss
def format_duration(ms):
    seconds = int(ms / 1000)
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02d}"

# Display each track in a Spotify-like format
for i, (_, track) in enumerate(top20.iterrows(), 1):
    cols = st.columns([0.1, 0.6, 0.15, 0.15])
    
    # Column 1: Track number
    with cols[0]:
        st.write(f"### {i}")
    
    # Column 2: Album cover and track info
    with cols[1]:
        col_img, col_info = st.columns([0.2, 0.8])
        with col_img:
            st.image(track['album_cover'], width=60)
        with col_info:
            st.write(f"**{track['track_name']}**")
            st.write(track['artist_names'])
    
    # Column 3: Release date
    with cols[2]:
        st.write(track['release_date'])
    
    # Column 4: Duration
    with cols[3]:
        st.write(format_duration(track['duration']))
    
    # Add a separator between tracks
    st.divider()