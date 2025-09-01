import numpy as np

class LoadData:
    def get_features():
        cosine_features = []
        count_features = []
        hr_features = []
        time_features = []

        with open('./outputs/features2/6_cosine_feature.out', 'r') as file:
            for line in file:
                cosine_features.append(float(line))

        with open('./outputs/features2/6_count_feature.out', 'r') as file:
            for line in file:
                count_features.append(float(line))

        with open('./outputs/features2/6_hr_feature.out', 'r') as file:
            for line in file:
                hr_features.append(float(line))

        with open('./outputs/features2/6_time_feature.out', 'r') as file:
            for line in file:
                time_features.append(float(line))
        
        if len(cosine_features) >= 20:
            data = []

            for index, i in enumerate(cosine_features[-20:-10]):
                temp_array = [
                    cosine_features[index], 
                    count_features[index], 
                    hr_features[index], 
                    time_features[index]
                ]
                data.append(np.array(temp_array))
            return data
        
        else:
            return None