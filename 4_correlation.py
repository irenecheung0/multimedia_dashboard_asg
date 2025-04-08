import streamlit as st
import pandas as pd

# Load custom CSS
def load_css():
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Apply custom CSS
load_css()


if ('data_weather_hk_rf' in st.session_state) and \
    ('data_weather_hk_heat' in st.session_state) and \
    ('data_weather_hk_rh' in st.session_state) and \
    ('data_spotify_hk' in st.session_state):
    df_hk_rf = st.session_state['data_weather_hk_rf']
    df_hk_heat = st.session_state['data_weather_hk_heat']
    df_hk_rh = st.session_state['data_weather_hk_rh']
    df_spotify_hk = st.session_state['data_spotify_hk']
else:
    st.switch_page("1_introduction.py")
    
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

def calculate_weather_audio_correlation(audio_feature):
    # Calculate average weekly metrics for each weather feature
    weekly_heat = df_hk_heat.groupby('YW')['normalizedValue'].mean().reset_index()
    weekly_heat.columns = ['report_date_YW', 'avg_heat']

    weekly_rain = df_hk_rf.groupby('YW')['normalizedValue'].mean().reset_index()
    weekly_rain.columns = ['report_date_YW', 'avg_rainfall']

    weekly_humidity = df_hk_rh.groupby('YW')['normalizedValue'].mean().reset_index()
    weekly_humidity.columns = ['report_date_YW', 'avg_humidity']

    # Calculate average weekly energy from Spotify data
    weekly_spotify = df_spotify_hk.groupby('report_date_YW')[audio_feature].mean().reset_index()

    # Merge all datasets
    weekly_data = weekly_spotify.merge(weekly_heat, on='report_date_YW', how='inner')
    weekly_data = weekly_data.merge(weekly_rain, on='report_date_YW', how='inner')
    weekly_data = weekly_data.merge(weekly_humidity, on='report_date_YW', how='inner')

    # Calculate correlation matrix
    weather_features = ['avg_heat', 'avg_rainfall', 'avg_humidity']
    correlation_matrix = weekly_data[[audio_feature] + weather_features].corr()

    # Display the results
    #st.subheader(f"Correlation Analysis: {audio_feature}")
    
    # Display correlation matrix as a table
    #st.dataframe(correlation_matrix.style.highlight_max(axis=0))
    
    # Create a heatmap-like visualization using Streamlit
    st.header(f'Weather Features vs {audio_feature}')
    
    # Convert correlation matrix to a format suitable for Streamlit
    corr_data = correlation_matrix.stack().reset_index()
    corr_data.columns = ['Variable 1', 'Variable 2', 'Correlation']
    
    # Display as a table with color formatting
    st.dataframe(
        correlation_matrix.style.background_gradient(
            cmap='coolwarm', 
            axis=None, 
            vmin=-1, 
            vmax=1
        ).format('{:.3f}')
    )


st.title("Correlation Analysis")

calculate_weather_audio_correlation("energy")
calculate_weather_audio_correlation("danceability")
calculate_weather_audio_correlation("acousticness")
calculate_weather_audio_correlation("valence")
calculate_weather_audio_correlation("loudness")
calculate_weather_audio_correlation("tempo")
calculate_weather_audio_correlation("speechiness")
calculate_weather_audio_correlation("liveness")