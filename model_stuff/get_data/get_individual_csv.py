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

    with open("outputs_lab/features/" + subject_number + "_cosine_feature.out", 'r') as file:
        for line in file:
            cosine_features.append(float(line))

    with open("outputs_lab/features/" + subject_number + "_count_feature.out", 'r') as file:
        for line in file:
            count_features.append(float(line))

    with open("outputs_lab/features/" + subject_number + "_hr_feature.out", 'r') as file:
        for line in file:
            parts = line.strip().split()
            hr_std_features.append(float(parts[0]))
            if len(parts) > 1:
                hr_mean_features.append(float(parts[1]))
            else:
                hr_mean_features.append(0.0)
            
    with open("outputs_lab/features/" + subject_number + "_time_feature.out", 'r') as file:
        for line in file:
            time_features.append(float(line))

    with open("outputs_lab/features/" + subject_number + "_psg_labels.out", 'r') as file:
        for line in file:
            line = line.strip()
            psg_labels.append(3 if int(float(line)) == 4 else int(float(line)))

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

    with open(f'model_stuff/data/test/individual/with_hr_mean/{i}.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)



