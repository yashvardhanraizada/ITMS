import pandas as pd
import numpy as np

events = pd.read_csv("congested-incident-DSM-Oct2016.csv")
inrix = pd.read_csv("DM_inrix_segments.csv")
sensors = pd.read_csv("dsm-sensors-wavetronix.csv")

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

def near_inrix(facility, dir, lat, lon):
    tmp_df = pd.DataFrame(inrix[(inrix.Facility == facility) & (inrix.Dir == dir)])
    if len(tmp_df.index) == 0:
        return "NA"
    tmp_df['Distance'] = haversine(lat, lon, tmp_df['Latitude'].values, tmp_df['Longitude'].values)
    tmp_df = tmp_df[tmp_df.Distance == tmp_df.Distance.min()]
    return tmp_df.iloc[0,0]

def near_sensor(facility, dir, lat, lon):
    tmp_df = pd.DataFrame(sensors[(sensors.Facility == facility) & (sensors.Dir == dir) & (haversine(lat, lon, sensors.Latitude ,sensors.Longitude) <= 1)])
    if len(tmp_df.index) == 0:
        return "NA"
    tmp_df['Distance'] = haversine(lat, lon, tmp_df['Latitude'].values, tmp_df['Longitude'].values)
    tmp_df = tmp_df[tmp_df.Distance == tmp_df.Distance.min()]
    return tmp_df.iloc[0,0]

series1 = []
series2 = []

for index, row in events.iterrows():
    series1.append(near_inrix(row['Facility'], row['Dir'], row['Latitude'], row['Longitude']))
    series2.append(near_sensor(row['Facility'], row['Dir'], row['Latitude'], row['Longitude']))

events['Nearest_Inrix'] = series1
events['Nearest_Wavetronix'] = series2

frames = [events['Date'], events['Event_ID'], events['Facility'], events['Dir'], events['Recv'], events['Cleared'], events['TotalTime'], events['Latitude'], events['Longitude'], events['Event.Type'], events['Nearest_Inrix'], events['Nearest_Wavetronix']]

df_final = pd.concat(frames, axis = 1)
df_final.to_csv('Nearest_Inrix_and_Wavetronix.csv')