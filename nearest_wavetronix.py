import pandas as pd
import numpy as np

inrix = pd.read_csv("DM_inrix_segments.csv")
sensors = pd.read_csv("dsm-sensors-wavetronix.csv")
events = inrix

# Define a basic Haversine distance formula
def haversine(lat1, lon1, lat2, lon2):
    MILES = 3959
    lat1, lon1, lat2, lon2 = map(np.deg2rad, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1 
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a)) 
    total_miles = MILES * c
    return total_miles

def near_sensor(facility, dir, lat, lon):
    tmp_df = pd.DataFrame(sensors[(sensors.Facility == facility) & (sensors.Dir == dir) & (haversine(lat, lon, sensors.Latitude ,sensors.Longitude) <= 1)])
    if len(tmp_df.index) == 0:
        return "NA"
    tmp_df['Distance'] = haversine(lat, lon, tmp_df['Latitude'].values, tmp_df['Longitude'].values)
    tmp_df = tmp_df[tmp_df.Distance == tmp_df.Distance.min()]
    return tmp_df.iloc[0,0]

series = []

for index, row in events.iterrows():
    series.append(near_sensor(row['Facility'], row['Dir'], row['Latitude'], row['Longitude']))

events['Nearest_Wavetronix'] = series
events.to_csv('Nearest_Wavetronix.csv', index = False)