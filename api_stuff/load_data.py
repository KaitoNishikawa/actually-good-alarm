import numpy as np
import math
import json
import pandas as pd
from sklearn.preprocessing import StandardScaler

class LoadData:
    def write_data_to_files(accelData, HRData, file_number_as_str, absolute_start_time):
        file_mode = 'a'

        print(f"timestamp: {accelData['timestamp'][0]}")
        # if new data session, reset files
        if accelData['timestamp'][0] < 10:
            file_mode = 'w'

        with open('data/motion/' + file_number_as_str + '_acceleration.txt', file_mode) as file:
            for index, i in enumerate(accelData['timestamp']):
                newLine = str(i) + ' ' + str(accelData['x'][index]) + ' ' + str(accelData['y'][index]) + ' ' + str(accelData['z'][index]) + '\n'
                file.write(newLine)
        with open('data/heart_rate/' + file_number_as_str + '_heartrate.txt', file_mode) as file:
            for index, i in enumerate(HRData['timestamp']):
                newLine = str(i) + ',' + str(HRData['HR'][index]) + '\n'
                file.write(newLine)
        with open('data/labels/' + file_number_as_str + '_labeled_sleep.txt', 'w') as file:
            iteration_amount = math.floor(accelData['timestamp'][-1] / 30) + 1

            for i in range(iteration_amount):
                newLine = str(i * 30) + ' ' + '0' + '\n'
                file.write(newLine)

        with open(f'sleep_data_logs/start_time_{file_number_as_str}.json', 'w') as f:
                json.dump({"startTime": absolute_start_time}, f)

    def get_features(file_number_as_str):
        cosine_features = []
        count_features = []
        hr_std_features = []
        hr_mean_features = []
        time_features = []

        with open('./outputs_apple/features/' + file_number_as_str +'_cosine_feature.out', 'r') as file:
            for line in file:
                cosine_features.append(float(line))

        with open('./outputs_apple/features/' + file_number_as_str +'_count_feature.out', 'r') as file:
            for line in file:
                count_features.append(float(line))

        with open("./outputs_apple/features/" + file_number_as_str + "_hr_feature.out", 'r') as file:
            for line in file:
                parts = line.strip().split()
                hr_std_features.append(float(parts[0]))
                if len(parts) > 1:
                    hr_mean_features.append(float(parts[1]))
                else:
                    hr_mean_features.append(0.0)

        with open('./outputs_apple/features/' + file_number_as_str +'_time_feature.out', 'r') as file:
            for line in file:
                time_features.append(float(line))
        


        if len(cosine_features) >= 20:
            df = pd.DataFrame({
                'cosine_feature': cosine_features[:-10],
                'count_feature': count_features[:-10],
                'hr_std': hr_std_features[:-10],
                'hr_mean': hr_mean_features[:-10],
                'time_feature': time_features[:-10],
            })

            df['count_feature_lag_1'] = df['count_feature'].shift(1)
            df['count_feature_lag_2'] = df['count_feature'].shift(2)

            df['hr_std_lag_1'] = df['hr_std'].shift(1)
            df['hr_std_lag_2'] = df['hr_std'].shift(2)

            df['hr_mean_lag_1'] = df['hr_mean'].shift(1)
            df['hr_mean_lag_2'] = df['hr_mean'].shift(2)

            df['hr_mean_delta'] = df['hr_mean'] - df['hr_mean'].shift(2)
            df = df.iloc[2:].reset_index(drop=True)

            scaler = StandardScaler()
            df['hr_mean_delta'] = scaler.fit_transform(df[['hr_mean_delta']])

            return df            
        else:
            return None