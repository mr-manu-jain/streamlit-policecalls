import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import os

@st.cache_data
def load_data(year):
    return pd.read_csv(f"analysis_yoy_analysis_{year}.csv")

@st.cache_data
def load_arrests_data():
    return pd.read_csv("analysis_arrests_data.csv")

st.title("Police Calls Analysis Dashboard")

available_years = [int(f.split('_')[-1].split('.')[0]) for f in os.listdir() if f.startswith('analysis_yoy_analysis_')]
available_years.sort()

selected_year = st.selectbox(
    "Select Year", 
    options=available_years,
    index=len(available_years) - 1
)

df = load_data(selected_year)
df['OFFENSE_DATE'] = pd.to_datetime(df['OFFENSE_DATE'])
df['Month'] = df['OFFENSE_DATE'].dt.month

# Bar Plot - Yearly Police Calls
st.header(f"Distribution of Number of Police Calls in {selected_year}")
calls_per_year = df.groupby('Year')['CALL_NUMBER'].count()

fig1, ax1 = plt.subplots(figsize=(10, 6))
sns.barplot(x=calls_per_year.index, y=calls_per_year.values, ax=ax1)
ax1.set_xlabel('Year')
ax1.set_ylabel('Number of Calls')
ax1.set_title(f'Distribution of Number of Police Calls in {selected_year}')
st.pyplot(fig1)

# Line Plot - Monthly Police Calls
monthly_calls = df.groupby('Month')['CALL_NUMBER'].count().reset_index()

st.header(f"Month-wise Distribution of Police Calls in {selected_year}")
fig2, ax2 = plt.subplots(figsize=(12, 6))
ax2.plot(monthly_calls['Month'], monthly_calls['CALL_NUMBER'], label=str(selected_year))

ax2.set_xlabel('Month')
ax2.set_ylabel('Number of Calls')
ax2.set_title(f'Month-wise Distribution of Police Calls in {selected_year}')
ax2.set_xticks(range(1, 13))
ax2.legend()
ax2.grid(True)
st.pyplot(fig2)

# Arrest Locations Map
st.header("Arrest Locations")

arrests_data = load_arrests_data()
arrests_data['latitude'] = pd.to_numeric(arrests_data['latitude'], errors='coerce')
arrests_data['longitude'] = pd.to_numeric(arrests_data['longitude'], errors='coerce')
arrests_data = arrests_data.dropna(subset=['latitude', 'longitude'])
arrests_data['Year'] = pd.to_datetime(arrests_data['START_DATE']).dt.year
arrests_data = arrests_data[arrests_data['Year'] == selected_year]

SJ_coordinates = [37.3382, -121.8863]
mymap = folium.Map(location=SJ_coordinates, zoom_start=12)
marker_cluster = MarkerCluster().add_to(mymap)

for _, row in arrests_data.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"Call Type: {row['CALL_TYPE']}<br>Date: {row['START_DATE']}",
    ).add_to(marker_cluster)

st_folium(mymap, width=700, height=500)
