import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
from pymongo import MongoClient
import datetime

# Load custom CSS
def load_css():
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Apply custom CSS
load_css()

st.title("Spotify Chart Data EDA")


if 'data_spotify_hk' in st.session_state:
    # Access the DataFrame
    df_spotify_hk = st.session_state['data_spotify_hk']
else:
    st.switch_page("1_introduction.py")


def convert_year_week_to_date(year_week):
    """
    Convert a year-week format (YYYY-WW) to the date of the first day of that week.
    
    Args:
        year_week (str): Year and week in 'YYYY-WW' format (e.g., '2022-01')
        
    Returns:
        str: Date string in 'YYYY-MM-DD' format for the first day (Monday) of that week
    """
    try:
        # Split the year-week string
        parts = year_week.split('-')
        if len(parts) != 2:
            return None
            
        year = int(parts[0])
        week = int(parts[1])
        
        # Validate year and week
        if not (1900 <= year <= 2100) or not (1 <= week <= 53):
            return None
        
        # Get the first day of the week (Monday is 1 in Python's isoweekday)
        # The %G and %V format codes represent ISO year and ISO week number
        first_day = datetime.datetime.strptime(f'{year}-{week}-1', '%G-%V-%u').date()
        return first_day.strftime('%Y-%m-%d')
    
    except (ValueError, TypeError) as e:
        # Handle potential parsing errors
        return None


def display_top_tracks_by_week():
    st.header("Top Tracks by Week", divider="grey")
    
    # Get unique weeks and sort them
    unique_weeks = sorted(df_spotify_hk['report_date_YW'].unique())
    
    # Create a dropdown for week selection
    selected_week = st.selectbox(
        "Select a week to view top tracks:",
        options=unique_weeks,
        index=len(unique_weeks)-1,  # Default to most recent week
        format_func=lambda x: f"{x} ({convert_year_week_to_date(x) or 'Unknown date'})"
    )
    
    # Filter dataframe for the selected week
    weekly_data = df_spotify_hk[df_spotify_hk['report_date_YW'] == selected_week]
    
    # Sort by rank and get top 10
    top_10_tracks = weekly_data.sort_values('rank').head(10)
    
    # Format duration from ms to MM:SS
    def format_duration(ms):
        seconds = int(ms / 1000)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    # Create a display dataframe with only the requested columns
    display_df = top_10_tracks[['rank', 'track_name', 'artist_individual', 'release_date', 'duration']].copy()
    
    # Format the duration column
    display_df['duration'] = display_df['duration'].apply(format_duration)
    
    # Format rank as integer
    display_df['rank'] = display_df['rank'].astype(int)
    
    # Rename columns for better display
    display_df = display_df.rename(columns={
        'rank': '#',
        'track_name': 'Track',
        'artist_individual': 'Artist',
        'release_date': 'Release Date',
        'duration': '🕐'
    })
    
    # Display the table
    st.subheader(f"Top 10 Tracks for Week {convert_year_week_to_date(selected_week) or 'Unknown date'}")
    
    # Create a cleaner, non-scrolling table using custom HTML
    col1, col2, col3, col4, col5 = st.columns([0.05, 0.35, 0.25, 0.15, 0.1])
    
    # Table headers
    with col1:
        st.write("**#**")
    with col2:
        st.write("**Track**")
    with col3:
        st.write("**Artist**")
    with col4:
        st.write("**Release Date**")
    with col5:
        st.write("**🕐**")
    
    # Table rows
    for _, row in display_df.iterrows():
        with col1:
            st.write(row['#'])
        with col2:
            st.write(row['Track'])
        with col3:
            st.write(row['Artist'])
        with col4:
            st.write(row['Release Date'])
        with col5:
            st.write(row['🕐'])


def plot_audio_features_time_series():
    
    st.header("Audio Features Time Series", divider="grey")
    
    # List of audio features to plot
    audio_features = ['danceability', 'energy', 'loudness', 'speechiness', 
                     'acousticness', 'liveness', 'valence', 'tempo']
    
    audio_features_description = {
        "danceability": {
            "title": "Danceability: The Rhythm of Movement", 
            "description": "This feature describes how suitable a track is for dancing based on musical elements like tempo, rhythm stability, beat strength, and overall regularity. A higher danceability score indicates a more danceable track."
        },
        "energy": {
            "title": "Energy: The Pulse of Intensity", 
            "description": "Representing the intensity and activity level of a track, this feature is often correlated with fast, loud, and noisy tracks. Tracks with high energy scores tend to be more upbeat and energetic."
        },
        "loudness": {
            "title": "Loudness: The Volume of Vibrations",
            "description": "Representing the overall loudness of a track in decibels (dB), this feature can be useful for audio normalization or volume adjustment purposes."
        },
        "speechiness": {
            "title": "Speechiness: The Measure of Words",
            "description": "Speechiness identifies tracks that contain spoken words, like podcasts or rap music. Higher values indicate more speech-like sounds, distinguishing them from purely instrumental tracks."
        },
        "acousticness": {
            "title": "Acousticness: The Echoes of Purity",
            "description": "This feature is a confidence measure of whether a track is acoustic. Tracks with higher acousticness scores are more likely to be acoustic, with little or no electronic elements."
        },
        "liveness": {
            "title": "Liveness: The Breath of Performance",
            "description": "Liveness detects the presence of an audience in the recording. A higher value suggests the track was performed live, offering a sense of authenticity and connection."
        },
        "valence": {
            "title": "Valence: The Spectrum of Emotions",
            "description": "Also known as the 'positiveness' score, valence describes the musical positiveness conveyed by a track. Tracks with higher valence scores tend to sound more positive, cheerful, and euphoric, while lower scores suggest more negative, sad, or depressing emotions."
        },
        "tempo": {
            "title": "Tempo: The Speed of Sound",
            "description": "The overall estimated tempo of a track, measured in beats per minute (BPM), can be crucial for applications like automatic DJ mixing or beat-synchronized visualizations."
        }
    }
    
    # Define festival dates to highlight
    festival_dates = ['2021-51', '2021-52', '2022-05', '2022-06']
    
    # Calculate weekly averages for each feature
    weekly_averages = {}
    for feature in audio_features:
        weekly_avg = df_spotify_hk.groupby('report_date_YW')[feature].mean().reset_index()
        
        # Normalize the feature values to 0-1 range for better visualization
        if feature != 'report_date_YW':
            min_val = weekly_avg[feature].min()
            max_val = weekly_avg[feature].max()
            # Avoid division by zero if min equals max
            if max_val > min_val:
                weekly_avg[f'{feature}_normalized'] = (weekly_avg[feature] - min_val) / (max_val - min_val)
            else:
                weekly_avg[f'{feature}_normalized'] = 0.5  # Default value if all values are the same
        
        weekly_averages[feature] = weekly_avg
    
    # Add dropdown to select audio feature
    selected_feature = st.selectbox(
        "Select Audio Feature to Visualize",
        options=audio_features,
        format_func=lambda x: audio_features_description[x]["title"]
    )
    
    # Display the title and description for the selected feature
    st.subheader(audio_features_description[selected_feature]["title"])
    st.write(audio_features_description[selected_feature]["description"])
    
    # Get data for the selected feature
    data = weekly_averages[selected_feature]
    
    # Create Altair chart with vertical lines for festivals
    base = alt.Chart(data).encode(
        x=alt.X('Week:N', title='Week', axis=alt.Axis(labelAngle=45), sort=None)
    ).transform_calculate(
        Week='datum.report_date_YW'
    )
    
    # Line chart for the normalized feature
    line = base.mark_line(point=True).encode(
        y=alt.Y(f'{selected_feature}_normalized:Q', title=f'Normalized {selected_feature}'),
        tooltip=[
            alt.Tooltip('Week:N', title='Week'),
            alt.Tooltip(f'{selected_feature}:Q', title=f'Original {selected_feature}', format='.2f'),
            alt.Tooltip(f'{selected_feature}_normalized:Q', title='Normalized Value', format='.2f')
        ]
    )
    
    # Create vertical rules for festival dates
    festival_rules = alt.Chart(
        pd.DataFrame({'report_date_YW': festival_dates})
    ).transform_calculate(
        Week='datum.report_date_YW'
    ).mark_rule(color='red', strokeDash=[3, 3]).encode(
        x='Week:N'
    )
    
    # Combine charts
    chart = (line + festival_rules).properties(
        width=700,
        height=300
    ).configure_view(
        strokeWidth=0
    )
    
    # Display the chart
    st.altair_chart(chart, use_container_width=True)
    st.caption(f"Min: {data[selected_feature].min():.2f}, Max: {data[selected_feature].max():.2f}")
    st.markdown("<span style='color:#ff0000; font-weight:bold;'>Red</span> vertical lines indicate festival periods.", unsafe_allow_html=True)

# Call the functions to generate the visualizations
display_top_tracks_by_week()
st.markdown("---")
plot_audio_features_time_series()