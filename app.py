import streamlit as st
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt

# Connect to MongoDB
client = MongoClient('mongo', 27017)
db = client['your_database']
collection = db['your_collection']

# Fetch data from MongoDB
data = pd.DataFrame(list(collection.find()))

# Display data using Streamlit
st.title('Data Visualization')
st.write(data)

# Plot a simple graph based on the 'Age' column
st.subheader('Age Distribution')
fig, ax = plt.subplots()
ax.hist(data['Age'], bins=20, edgecolor='black')
ax.set_xlabel('Age')
ax.set_ylabel('Frequency')
ax.set_title('Distribution of Age')

# Display the plot in Streamlit
st.pyplot(fig)