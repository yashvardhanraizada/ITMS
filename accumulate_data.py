# Import sytem files, packages & utilities
import time
tic = time.time()
import datetime
import pandas as pd
import numpy as np
import scipy.stats

print(str(time.time() - tic) + " seconds : " + "Data Accumulator : version - 2020.06.27")
print(str(time.time() - tic) + " seconds : " + "Copyright 2020 YVR Systems & Solutions Ltd. All Rights Reserved ...")
print(str(time.time() - tic) + " seconds : " + "Loading Data ...")
# Load Data from .csv files
inrix = pd.read_csv("inrix-oct-nov.csv", dtype = {'Code':'int', 'Time':'str', 'Conf':'int', 'Cvalue':'int', 'Speed':'int'})
sensor = pd.read_csv("DM_data_wave_aug-oct-sample.csv", header = None, usecols = [0,1,5], names = ['Code', 'Speed', 'Time'], dtype={'Code':'str', 'Speed':'float', 'Time':'str'})
events = pd.read_csv("Nearest_Wavetronix.csv", usecols=[0,5], dtype={'Code':'int', 'Nearest_Wavetronix':'str'})
org_events = pd.read_csv("Nearest_Inrix_and_Wavetronix.csv", usecols = [5,6,11], dtype={'Recv':'str', 'Cleared':'str', 'Nearest_Inrix':'int'})
threshold_inr = pd.read_csv("weekly-thresh-inrix-oct-nov.csv", usecols=[0,1,2,3,4,5,6,8], dtype={'Code':'int','weekday':'int','hour':'int','period':'int','mean_cal':'float','std_cal':'float','med_cal':'float','iqd_cal':'float'})
threshold_wav = pd.read_csv("weekly-thresh-wave-oct.csv", usecols=[0,1,2,3,4,5,6,8], dtype={'Code':'str','weekday':'int','hour':'int','period':'int','mean_cal':'float','std_cal':'float','med_cal':'float','iqd_cal':'float'})

print(str(time.time() - tic) + " seconds : " + "Preparing Functions ...")
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
    series_med = []
    series_iqd = []
    series_mean = []
    series_std = []

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
        med = temp_thresh['med_cal'].mean()
        iqd = temp_thresh['iqd_cal'].mean()
        mean_val = temp_thresh['mean_cal'].mean()
        std = temp_thresh['std_cal'].mean()
        threshold = temp_thresh['Threshold'].mean()
        series += l * [threshold]
        series_med += l * [med]
        series_iqd += l * [iqd]
        series_mean += l * [mean_val]
        series_std += l * [std]
        i += 12
    tmp_df['In_Threshold'] = series
    tmp_df['In_Med'] = series_med
    tmp_df['In_Iqd'] = series_iqd
    tmp_df['In_Mean'] = series_mean
    tmp_df['In_Std'] = series_std
    tmp_df['In_Med_Pnorm'] = 1 - scipy.stats.norm(tmp_df['In_Med'], tmp_df['In_Iqd']).cdf(tmp_df['Speed'])
    tmp_df['In_Mean_Pnorm'] = 1 - scipy.stats.norm(tmp_df['In_Mean'], tmp_df['In_Std']).cdf(tmp_df['Speed'])
    tmp_df.drop(columns = ['Conf', 'Cvalue'], inplace = True)
    tmp_df.rename(columns = {'Code' : 'In_Code', 'Speed' : 'In_Speed'}, inplace = True)
    return tmp_df

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
    series_med = []
    series_iqd = []
    series_mean = []
    series_std = []

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
        med = temp_thresh['med_cal'].mean()
        iqd = temp_thresh['iqd_cal'].mean()
        mean_val = temp_thresh['mean_cal'].mean()
        std = temp_thresh['std_cal'].mean()
        threshold = temp_thresh['Threshold'].mean()
        series += l * [threshold]
        series_med += l * [med]
        series_iqd += l * [iqd]
        series_mean += l * [mean_val]
        series_std += l * [std]
        i += 36
    tmp_df['Wv_Threshold'] = series
    tmp_df['Wv_Med'] = series_med
    tmp_df['Wv_Iqd'] = series_iqd
    tmp_df['Wv_Mean'] = series_mean
    tmp_df['Wv_Std'] = series_std
    tmp_df['Wv_Med_Pnorm'] = 1 - scipy.stats.norm(tmp_df['Wv_Med'], tmp_df['Wv_Iqd']).cdf(tmp_df['Speed'])
    tmp_df['Wv_Mean_Pnorm'] = 1 - scipy.stats.norm(tmp_df['Wv_Mean'], tmp_df['Wv_Std']).cdf(tmp_df['Speed'])
    tmp_df.rename(columns = {'Code' : 'Wv_Code', 'Speed' : 'Wv_Speed'}, inplace = True)
    tmp_df['Time'] = tmp_df['Time'].dt.tz_localize(None)
    return tmp_df

print(str(time.time() - tic) + " seconds : " + "Just Starting ...")
# Specify Start Date
start_date = datetime.datetime(2016,10,1)

# Specify End Date
end_date = datetime.datetime(2016,10,31)

# Specify Interval of Analysis
delta = datetime.timedelta(days=1)

# Preparing Incident Marking Data
org_events['Recv'] = pd.to_datetime(org_events['Recv'])
org_events['Cleared'] = pd.to_datetime(org_events['Cleared'])

# Convert to .csv file (Specify "Name" of the File)
file_name = 'October_2016_Data.csv'

file_data = pd.DataFrame(columns=['Time','In_Code','Wv_Code','In_Speed','Wv_Speed','In_Threshold','Wv_Threshold','In_Med','Wv_Med','In_Iqd','Wv_Iqd','In_Mean','Wv_Mean','In_Std','Wv_Std','In_Med_Pnorm','Wv_Med_Pnorm','In_Mean_Pnorm','Wv_Mean_Pnorm','Comb_Median_Prob','Comb_Mean_Prob','Org_Inc'])
file_data.to_csv(file_name, index = False)
print(str(time.time() - tic) + " seconds : " + "Data being saved in File : " + file_name)

print(str(time.time() - tic) + " seconds : " + "Just Started ...")
# Begin iterating to collect Data for each Date
while start_date <= end_date:
    # Iterate through Inrix Segments & collect Data for each segment
    for index, row in events.iterrows():
        probability_in = inrix_threshold(row['Code'], start_date)

        if row['Nearest_Wavetronix'] == "NA" :
            probability_wv = pd.DataFrame(columns=['Wv_Code','Wv_Speed','Time','Wv_Threshold','Wv_Med','Wv_Iqd','Wv_Mean','Wv_Std','Wv_Med_Pnorm','Wv_Mean_Pnorm'])
        else :
            probability_wv = wavetronix_threshold(row['Nearest_Wavetronix'], start_date)
        
        # Left-Join of Inrix & Wavetronix Data
        big_data = pd.merge(left=probability_in, right=probability_wv, how='left', left_on='Time', right_on='Time')

        # Combined Probability
        big_data['Comb_Median_Prob'] = big_data['In_Med_Pnorm'] * big_data['Wv_Med_Pnorm']
        big_data['Comb_Mean_Prob'] = big_data['In_Mean_Pnorm'] * big_data['Wv_Mean_Pnorm']

        # Rearranging & Original Incident column inititation
        big_data = big_data[['Time','In_Code','Wv_Code','In_Speed','Wv_Speed','In_Threshold','Wv_Threshold','In_Med','Wv_Med','In_Iqd','Wv_Iqd','In_Mean','Wv_Mean','In_Std','Wv_Std','In_Med_Pnorm','Wv_Med_Pnorm','In_Mean_Pnorm','Wv_Mean_Pnorm','Comb_Median_Prob','Comb_Mean_Prob']]
        big_data['Org_Inc'] = 0

        # Marking original incidents as 1
        tmp = org_events[(org_events['Nearest_Inrix'] == row['Code']) & (org_events.Recv.dt.date == start_date.date())]
        if len(tmp.index) > 0 :
            for index, row in tmp.iterrows():
                big_data.loc[(big_data['In_Code'] == row['Nearest_Inrix']) & (big_data['Time'] >= row['Recv']) & (big_data['Time'] <= row['Cleared']), 'Org_Inc'] = 1

        # Appending Result DataFrames
        big_data.to_csv(file_name, mode='a', index = False, header = False)
    
    print(str(time.time() - tic) + " seconds : " + str(start_date) + " Data Collected Successfully ...")
    # Update Date
    start_date += delta

print(str(time.time() - tic) + " seconds : " + "Just Finishing Up ...")
print(str(time.time() - tic) + " seconds : " + "Finished !")
print(str(time.time() - tic) + " seconds : " + "Task completed successfully !!!")