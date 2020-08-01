import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

inrix = pd.read_csv("inrix-oct-nov.csv", dtype = {'Code':'int', 'Time':'str', 'Conf':'int', 'Cvalue':'int', 'Speed':'int'})
sensor = pd.read_csv("DM_data_wave_aug-oct-sample.csv", header = None, usecols = [0,1,5], names = ['Code', 'Speed', 'Time'], dtype={'Code':'str', 'Speed':'float', 'Time':'str'})
incidents = pd.read_csv("Nearest_Inrix_and_Wavetronix.csv")
threshold_inr = pd.read_csv("weekly-thresh-inrix-oct-nov.csv", usecols=[0,1,2,3,6,8], dtype={'Code':'int','weekday':'int','hour':'int','period':'int','med_cal':'float','iqd_cal':'float'})
threshold_wav = pd.read_csv("weekly-thresh-wave-oct.csv", usecols=[0,1,2,3,6,8], dtype={'Code':'str','weekday':'int','hour':'int','period':'int','med_cal':'float','iqd_cal':'float'})

def inrix_threshold(inrix_code, incident_date):
    ts = pd.to_datetime(incident_date)
    tmp_df = pd.DataFrame(inrix[(inrix.Code == int(inrix_code)) & (inrix.Conf == 30) & (inrix.Cvalue >= 30)])
    tmp_df['Time'] = pd.to_datetime(tmp_df['Time'])
    tmp_df = tmp_df[tmp_df.Time.dt.date == ts.date()]
    tmp_df = tmp_df.sort_values(by = 'Time')
    threshold_in = pd.DataFrame(threshold_inr[(threshold_inr.Code == int(inrix_code)) & (threshold_inr.weekday == int(ts.weekday()) + 1)])
    threshold_in['Time'] = pd.to_timedelta(threshold_in['hour'], unit = 'h') + pd.to_timedelta(threshold_in['period']*12, unit = 'm')
    threshold_in['Threshold'] = threshold_in['med_cal'] - threshold_in['iqd_cal']*2

    series = []
    i = 0
    while i < len(tmp_df.index):
        if (i + 12) <= len(tmp_df.index):
            l = 12
        else:
            l = len(tmp_df.index) % 12
        t1 = tmp_df.iloc[i,1]
        t2 = tmp_df.iloc[i+l-1,1]
        min_time = pd.to_timedelta(str(t1.time()))
        max_time = pd.to_timedelta(str(t2.time()))
        temp_thresh = threshold_in[(threshold_in.Time >= min_time) & (threshold_in.Time <= max_time)]
        threshold = temp_thresh['Threshold'].mean()
        series += l * [threshold]
        i += 12
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
    threshold_wv = pd.DataFrame(threshold_wav[(threshold_wav.Code == str(wavetronix_code)) & (threshold_wav.weekday == int(ts.weekday()) + 1)])
    threshold_wv['Time'] = pd.to_timedelta(threshold_wv['hour'], unit = 'h') + pd.to_timedelta(threshold_wv['period']*12, unit = 'm')
    threshold_wv['Threshold'] = threshold_wv['med_cal'] - threshold_wv['iqd_cal']*2

    series = []
    i = 0
    while i < len(tmp_df.index):
        if (i + 36) <= len(tmp_df.index):
            l = 36
        else:
            l = len(tmp_df.index) % 36
        t1 = tmp_df.iloc[i,2]
        t2 = tmp_df.iloc[i+l-1,2]
        min_time = pd.to_timedelta(str(t1.time()))
        max_time = pd.to_timedelta(str(t2.time()))
        temp_thresh = threshold_wv[(threshold_wv.Time >= min_time) & (threshold_wv.Time <= max_time)]
        threshold = temp_thresh['Threshold'].mean()
        series += l * [threshold]
        i += 36
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