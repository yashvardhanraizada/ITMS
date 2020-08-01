import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

inrix = pd.read_csv("inrix-oct-nov.csv", dtype = {'Code':'int', 'Time':'str', 'Conf':'int', 'Cvalue':'int', 'Speed':'int'})
sensor = pd.read_csv("DM_data_wave_aug-oct-sample.csv", header = None, usecols = [0,1,5], names = ['Code', 'Speed', 'Time'], dtype={'Code':'str', 'Speed':'float', 'Time':'str'})
incidents = pd.read_csv("Nearest_Inrix_and_Wavetronix.csv")

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
    plt.suptitle('Inrix_Data_Analysis' + ' [Event ID : ' + str(incident_id) + ']')
    plt.title('Duration : ' + str(start_time) + ' to ' + str(end_time) + ' [Inrix Code : ' + str(inrix_code) + ']')
    plt.xlabel('Timestamp (MM-DD-YYYY Hrs:Min:Sec)')
    plt.ylabel('Speed & Threshold')

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
    plt.suptitle('Wavetronix_Data_Analysis' + ' [Event ID : ' + str(incident_id) + ']')
    plt.title('Duration : ' + str(start_time) + ' to ' + str(end_time) + ' [Wavetronix Code : ' + str(wavetronix_code) + ']')
    plt.xlabel('Timestamp (MM-DD-YYYY Hrs:Min:Sec)')
    plt.ylabel('Speed & Threshold')

run = True
while run == True :
    print("Press only 'Enter' key to continue ...")
    print("Type 'exit' and press 'Enter' key to close the program ...")
    option = str(input())
    if option == 'exit' :
        run = False
    else :
        incident_id = int(input("Enter Event-ID : "))
        df = pd.concat([incidents['Event_ID'], incidents['Date'], incidents['Nearest_Inrix'], incidents['Nearest_Wavetronix'], incidents['Recv'], incidents['Cleared']], axis = 1)
        df = df[df.Event_ID == incident_id]
        df['Recv'] = pd.to_datetime(df['Recv'])
        df['Cleared'] = pd.to_datetime(df['Cleared'])
        df['Date'] = pd.to_datetime(df['Date'])
        if len(df.index) == 0:
            print("Invalid Event-ID")
        else:
            start_time = df.iloc[0,4]
            end_time = df.iloc[0,5]
            inrix_threshold(df.iloc[0,2], df.iloc[0,1])
            wavetronix_threshold(df.iloc[0,3], df.iloc[0,1])
            plt.show()