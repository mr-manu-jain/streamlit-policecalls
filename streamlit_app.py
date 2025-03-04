import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from google.cloud import bigquery
import json
from google.oauth2 import service_account
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# Load Google Cloud credentials from Streamlit Secrets
gcp_credentials = json.loads(st.secrets["gcp"]["service_account"])

# Authenticate using the credentials
credentials = service_account.Credentials.from_service_account_info(gcp_credentials)

# Set up BigQuery client with the credentials
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Fetch Data
query = """
SELECT * FROM `solid-saga-452604-c8.policecalls_dataset.yoy_analysis`
"""
df = client.query(query).to_dataframe()

# Ensure 'OFFENSE_DATE' is datetime
df['OFFENSE_DATE'] = pd.to_datetime(df['OFFENSE_DATE'])
analysis1 = df.copy()
analysis1['Year'] = analysis1['OFFENSE_DATE'].dt.year
analysis1['Month'] = analysis1['OFFENSE_DATE'].dt.month
calls_per_year = analysis1.groupby('Year')['CALL_NUMBER'].count()


st.title("Police Calls Analysis Dashboard")
selected_year = st.selectbox(
    "Select Year", 
    options=sorted(analysis1['Year'].unique()), 
    index=len(analysis1['Year'].unique()) - 1
)
filtered_data = analysis1[analysis1['Year'] == selected_year]
st.header(f"Distribution of Number of Police Calls in {selected_year}")
calls_per_year = filtered_data.groupby('Year')['CALL_NUMBER'].count()
fig1, ax1 = plt.subplots(figsize=(10, 6))
sns.barplot(x=calls_per_year.index, y=calls_per_year.values, ax=ax1)
ax1.set_xlabel('Year')
ax1.set_ylabel('Number of Calls')
ax1.set_title(f'Distribution of Number of Police Calls in {selected_year}')
st.pyplot(fig1)

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

st.header("Arrest Locations")
arrests_data_query = """
SELECT * FROM `solid-saga-452604-c8.policecalls_dataset.arrests_data`;
"""
query_job = client.query(arrests_data_query)
res = query_job.result()
arrests_data = res.to_dataframe()
arrests_data['latitude'] = pd.to_numeric(arrests_data['latitude'], errors='coerce')
arrests_data['longitude'] = pd.to_numeric(arrests_data['longitude'], errors='coerce')
arrests_data = arrests_data.dropna(subset=['latitude', 'longitude'])
arrests_data['Year'] = pd.to_datetime(arrests_data['START_DATE']).dt.year

# Create a map centered on San Jose
SJ_coordinates = [37.3382, -121.8863]
map_center =  [SJ_coordinates[0], SJ_coordinates[1]]
mymap = folium.Map(location=map_center, zoom_start=12)

marker_cluster = MarkerCluster().add_to(mymap)
for _,row in arrests_data.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"Call Type: {row['CALL_TYPE']}<br>Date: {row['START_DATE']}",
    ).add_to(marker_cluster)

st_folium(mymap, width=700, height=500)
