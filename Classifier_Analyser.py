import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix 
from sklearn.metrics import accuracy_score 
from sklearn.metrics import classification_report

data = pd.read_csv("October_2016_Data.csv", usecols = [19,20,21])

#print(data)

# Cleaning up
data.dropna(subset = ['Comb_Median_Prob', 'Comb_Mean_Prob'], inplace = True)
data['Comb_Median_Prob'] = data['Comb_Median_Prob'].astype('float')
data['Comb_Mean_Prob'] = data['Comb_Mean_Prob'].astype('float')

#print(data)

# Specify threshold probability for incident detection
thresh_prob = 0.4

data['Comb_Median_Prob'] = data['Comb_Median_Prob'].apply(lambda x: 1 if x >= thresh_prob else 0)
data['Comb_Mean_Prob'] = data['Comb_Mean_Prob'].apply(lambda x:  1 if x >= thresh_prob else 0)

#print(data)

print('For Threshold Probability of Alarm set to : ' + str(thresh_prob))

print('Confusion Matrix (Median & IQD Method) :')
# results = confusion_matrix(actual, predicted)
results = confusion_matrix(data['Org_Inc'], data['Comb_Median_Prob']) 
print(results) 
print('Accuracy Score :',accuracy_score(data['Org_Inc'], data['Comb_Median_Prob'])) 
print('Report : ')
print(classification_report(data['Org_Inc'], data['Comb_Median_Prob'])) 

print('Confusion Matrix (Mean & STD Method) :')
# results = confusion_matrix(actual, predicted)
results1 = confusion_matrix(data['Org_Inc'], data['Comb_Mean_Prob']) 
print(results1) 
print('Accuracy Score :',accuracy_score(data['Org_Inc'], data['Comb_Mean_Prob'])) 
print('Report : ')
print(classification_report(data['Org_Inc'], data['Comb_Mean_Prob'])) 