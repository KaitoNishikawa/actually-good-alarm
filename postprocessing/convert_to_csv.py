import csv

# subjects_as_ints = [
#     46343, 759667, 781756, 844359, 1066528, 1360686, 1449548, 1455390,
#     1818471, 2598705, 2638030, 3509524, 3997827, 4018081, 4314139, 4426783,
#     5132496, 5383425, 5498603, 5797046, 6220552, 7749105, 8000685, 8173033,
#     8258170, 8530312, 8686948, 8692923, 9106476, 9618981, 9961348
# ]
subjects_as_ints = [
    46343, 759667, 781756, 844359, 1066528, 1360686, 1449548, 1455390,
    1818471, 2598705, 2638030, 3509524, 3997827, 4018081, 4314139, 4426783,
    5132496, 5383425, 5498603, 5797046, 6220552, 7749105, 8000685, 8173033,
    8258170, 8530312, 8686948, 8692923
]

print(len(subjects_as_ints))

labels = ['cosine_feature', 'count_feature', 'hr_std', 'hr_mean', 'time_feature', 'psg_label']
cosine_features = []
count_features = []
hr_std_features = []
hr_mean_features = []
time_features = []
psg_labels = []

for i in subjects_as_ints:
    subject_number = str(i)

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
            # if int(float(line)) == 4:
            #     print(f'subject {subject_number}')
            #     print(line)

    # print(len(cosine_features))
    # print(len(count_features))
    # print(len(hr_features))
    # print(len(time_features))
    # print(len(psg_labels))

data = []
data.append(labels)

for index, i in enumerate(cosine_features):
    newArray = []
    newArray.append(cosine_features[index])
    newArray.append(count_features[index])
    newArray.append(hr_std_features[index])
    newArray.append(hr_mean_features[index])
    newArray.append(time_features[index])
    newArray.append(psg_labels[index])

    data.append(newArray)

with open('postprocessing/data/bigboy.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(data)



