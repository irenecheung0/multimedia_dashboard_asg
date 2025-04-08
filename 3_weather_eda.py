import streamlit as st
import pandas as pd
from pymongo import MongoClient

# Load custom CSS
def load_css():
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Apply custom CSS
load_css()


st.title("Weather Data EDA")

if ('data_weather_hk_rf' in st.session_state) and \
    ('data_weather_hk_heat' in st.session_state) and \
    ('data_weather_hk_rh' in st.session_state):
    df_hk_rf = st.session_state['data_weather_hk_rf']
    df_hk_heat = st.session_state['data_weather_hk_heat']
    df_hk_rh = st.session_state['data_weather_hk_rh']
else:
    st.switch_page("1_introduction.py")


def plot_normalized_time_series(df, title=None):
    """
    Plot normalized values over time by Year-Week using Streamlit
    
    Args:
        df: DataFrame containing 'YW' and 'normalizedValue' columns
        title: Optional title for the plot
    """
    # Sort by YW to ensure proper chronological order
    df_sorted = df.sort_values('YW')
    
    # Set the chart title
    if title:
        st.subheader(title)
    else:
        st.subheader('Values Over Time')
    
    # Create a copy of the dataframe for plotting
    chart_df = df_sorted.copy()
    chart_df = chart_df.set_index('YW')
    
    # Display the line chart
    st.line_chart(chart_df['Value'])
    
    # Optionally show year markers
    years = df_sorted['YW'].str[:4].unique()
    if len(years) > 1:
        st.caption(f"Chart spans from {min(years)} to {max(years)}")


# st.title('RF')
# st.write(df_hk_rf)
# st.title('Heat')
# st.write(df_hk_heat)
# st.title('RH')
# st.write(df_hk_rh)
plot_normalized_time_series(df_hk_rf, 'Total Rainfall (mm) over Time')
plot_normalized_time_series(df_hk_heat, 'Mean HKHI(°C) over Time')
plot_normalized_time_series(df_hk_rh, 'Mean Relative Humidity (%) over Time')
