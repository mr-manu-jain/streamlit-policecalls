import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# Load Data from Local CSV Files
df = pd.read_csv("analysis_yoy_analysis.csv")  # Ensure this file is in the same directory
arrests_data = pd.read_csv("analysis_arrests_data.csv")  # Ensure this file is in the same directory

# Ensure 'OFFENSE_DATE' is datetime
df['OFFENSE_DATE'] = pd.to_datetime(df['OFFENSE_DATE'])

# Data Preparation
analysis1 = df.copy()
analysis1['Year'] = analysis1['OFFENSE_DATE'].dt.year
analysis1['Month'] = analysis1['OFFENSE_DATE'].dt.month
calls_per_year = analysis1.groupby('Year')['CALL_NUMBER'].count()

# Streamlit UI
st.title("Police Calls Analysis Dashboard")

selected_year = st.selectbox(
    "Select Year", 
    options=sorted(analysis1['Year'].unique()), 
    index=len(analysis1['Year'].unique()) - 1
)
filtered_data = analysis1[analysis1['Year'] == selected_year]

# Bar Plot - Yearly Police Calls
st.header(f"Distribution of Number of Police Calls in {selected_year}")
calls_per_year = filtered_data.groupby('Year')['CALL_NUMBER'].count()

fig1, ax1 = plt.subplots(figsize=(10, 6))
sns.barplot(x=calls_per_year.index, y=calls_per_year.values, ax=ax1)
ax1.set_xlabel('Year')
ax1.set_ylabel('Number of Calls')
ax1.set_title(f'Distribution of Number of Police Calls in {selected_year}')
st.pyplot(fig1)

# Line Plot - Monthly Police Calls
monthly_calls = filtered_data.groupby(['Year', 'Month'])['CALL_NUMBER'].count().reset_index()

st.header(f"Month-wise Distribution of Police Calls in {selected_year}")
fig2, ax2 = plt.subplots(figsize=(12, 6))
year_data = monthly_calls[monthly_calls['Year'] == selected_year]
ax2.plot(year_data['Month'], year_data['CALL_NUMBER'], label=str(selected_year))

ax2.set_xlabel('Month')
ax2.set_ylabel('Number of Calls')
ax2.set_title(f'Month-wise Distribution of Police Calls in {selected_year}')
ax2.set_xticks(range(1, 13))
ax2.legend()
ax2.grid(True)
st.pyplot(fig2)

# Arrest Locations Map
st.header("Arrest Locations")

# Ensure latitude & longitude are numeric and remove NaN values
arrests_data['latitude'] = pd.to_numeric(arrests_data['latitude'], errors='coerce')
arrests_data['longitude'] = pd.to_numeric(arrests_data['longitude'], errors='coerce')
arrests_data = arrests_data.dropna(subset=['latitude', 'longitude'])

# Convert date column to extract the year
arrests_data['Year'] = pd.to_datetime(arrests_data['START_DATE']).dt.year

# Create a map centered on San Jose
SJ_coordinates = [37.3382, -121.8863]
map_center = [SJ_coordinates[0], SJ_coordinates[1]]
mymap = folium.Map(location=map_center, zoom_start=12)

marker_cluster = MarkerCluster().add_to(mymap)

# Add markers to the map
for _, row in arrests_data.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"Call Type: {row['CALL_TYPE']}<br>Date: {row['START_DATE']}",
    ).add_to(marker_cluster)

st_folium(mymap, width=700, height=500)
