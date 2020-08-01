import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

inrix = pd.read_csv("inrix-oct-nov.csv")
wave = pd.read_csv("DM_data_wave_aug-oct-sample.csv", header = None)
incidents = pd.read_csv("Nearest_Inrix_and_Wavetronix.csv")

sensor = pd.DataFrame(columns = ['Code', 'Speed', 'Time'])
sensor['Code'] = wave[0]
sensor['Speed'] = wave[1]
sensor['Time'] = wave[5]

def inrix_threshold(inrix_code, incident_date):
    ts = pd.to_datetime(incident_date)
    tmp_df = pd.DataFrame(inrix[(inrix.Code == int(inrix_code)) & (inrix.Conf == 30) & (inrix.Cvalue >= 30)])
    tmp_df['Time'] = pd.to_datetime(tmp_df['Time'])
    tmp_df = tmp_df[tmp_df.Time.dt.date == ts.date()]
    tmp_df = tmp_df.sort_values(by = 'Time')
    series = []
    i = 0
    while i < len(tmp_df.index):
        if (i + 15) <= len(tmp_df.index):
            l = 15
        else:
            l = len(tmp_df.index) % 15
        temp = tmp_df[i : i+l]
        med = temp['Speed'].median()
        iqd = temp['Speed'].quantile(0.75) - temp['Speed'].quantile(0.25)
        threshold = med - 2*iqd
        series += l * [threshold]
        i += 15
    tmp_df['Threshold'] = series
    tmp_df.plot(x = 'Time', y = ['Speed', 'Threshold'])
    plt.title('[Inrix_Data_Analysis] ' + 'Code : ' + str(inrix_code))
    plt.xlabel('Date-Time')
    plt.ylabel('Speed')

def wavetronix_threshold(wavetronix_code, incident_date):
    ts = pd.to_datetime(incident_date)
    tmp_df = pd.DataFrame(sensor[sensor.Code == str(wavetronix_code)])
    tmp_df['Time'] = pd.to_datetime(tmp_df['Time'])
    tmp_df = tmp_df[tmp_df.Time.dt.date == ts.date()]
    tmp_df = tmp_df.sort_values(by = 'Time')
    series = []
    i = 0
    while i < len(tmp_df.index):
        if (i + 45) <= len(tmp_df.index):
            l = 45
        else:
            l = len(tmp_df.index) % 45
        temp = tmp_df[i : i+l]
        med = temp['Speed'].median()
        iqd = temp['Speed'].quantile(0.75) - temp['Speed'].quantile(0.25)
        threshold = med - 2*iqd
        series += l * [threshold]
        i += 45
    tmp_df['Threshold'] = series
    tmp_df.plot(x = 'Time', y = ['Speed', 'Threshold'])
    plt.title('[Wavetronix_Data_Analysis] ' + 'Code : ' + str(wavetronix_code))
    plt.xlabel('Date-Time')
    plt.ylabel('Speed')

incident_id = int(input("Enter Incident-ID : "))
df = pd.concat([incidents['Event_ID'], incidents['Date'], incidents['Nearest_Inrix'], incidents['Nearest_Wavetronix']], axis = 1)
df = df[df.Event_ID == incident_id]
df['Date'] = pd.to_datetime(df['Date'])
if len(df.index) == 0:
    print("Invalid Incident-ID")
else:
    inrix_threshold(df.iloc[0,2], df.iloc[0,1])
    wavetronix_threshold(df.iloc[0,3], df.iloc[0,1])
    plt.show()