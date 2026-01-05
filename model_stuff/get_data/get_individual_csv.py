import numpy as np
import csv

subjects_as_ints = [
    9106476, 9618981, 9961348
]

print(len(subjects_as_ints))

labels = ['cosine_feature', 'count_feature', 'hr_std', 'hr_mean', 'time_feature', 'psg_label']


for i in subjects_as_ints:
    subject_number = str(i)
    cosine_features = []
    count_features = []
    hr_std_features = []
    hr_mean_features = []
    time_features = []
    psg_labels = []

    cosine = np.load("outputs_lab/features/" + subject_number + "_cosine_feature.npy")
    cosine_features = cosine.tolist()

    count = np.load("outputs_lab/features/" + subject_number + "_count_feature.npy")
    count_features = count.tolist()

    hr_std = np.load("outputs_lab/features/" + subject_number + "_hr_feature.npy")
    hr_std_features = hr_std.tolist()
    
    hr_mean = np.load("outputs_lab/features/" + subject_number + "_hr_mean_feature.npy")
    hr_mean_features = hr_mean.tolist()
            
    time = np.load("outputs_lab/features/" + subject_number + "_time_feature.npy")
    time_features = time.tolist()

    psg = np.load("outputs_lab/features/" + subject_number + "_psg_labels.npy")
    psg = np.where(psg == 4, 3, psg)  
    psg_labels = psg.astype(int).tolist()

    data = []
    data.append(labels)

    for index, j in enumerate(cosine_features):
        newArray = []
        newArray.append(cosine_features[index])
        newArray.append(count_features[index])
        newArray.append(hr_std_features[index])
        newArray.append(hr_mean_features[index])
        newArray.append(time_features[index])
        newArray.append(psg_labels[index])

        data.append(newArray)

    with open(f'model_stuff/data/test/individual/new_time_window/{i}.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)



