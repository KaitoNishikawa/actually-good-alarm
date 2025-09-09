import numpy as np
import math

class LoadData:
    def write_data_to_files(accelData, HRData, file_number_as_str):
        file_mode = 'a'

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

    def get_features(file_number_as_str):
        cosine_features = []
        count_features = []
        hr_features = []
        time_features = []

        with open('./outputs/features2/' + file_number_as_str +'_cosine_feature.out', 'r') as file:
            for line in file:
                cosine_features.append(float(line))

        with open('./outputs/features2/' + file_number_as_str +'_count_feature.out', 'r') as file:
            for line in file:
                count_features.append(float(line))

        with open('./outputs/features2/' + file_number_as_str +'_hr_feature.out', 'r') as file:
            for line in file:
                hr_features.append(float(line))

        with open('./outputs/features2/' + file_number_as_str +'_time_feature.out', 'r') as file:
            for line in file:
                time_features.append(float(line))
        


        if len(cosine_features) >= 20:
            data = []
            index_offset = len(cosine_features) - 20

            for index, i in enumerate(cosine_features[-20:-10]):
                temp_array = [
                    cosine_features[index + index_offset], 
                    count_features[index + index_offset], 
                    hr_features[index + index_offset], 
                    time_features[index + index_offset]
                ]
                data.append(np.array(temp_array))

            return data                
        else:
            return None