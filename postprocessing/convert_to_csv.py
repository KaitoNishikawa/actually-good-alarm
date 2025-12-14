import csv

subjects_as_ints = [3509524, 5132496, 1066528, 5498603, 2638030, 2598705, 5383425, 1455390, 4018081, 9961348,
                            1449548, 8258170, 781756, 9106476, 8686948, 8530312, 3997827, 4314139, 1818471, 4426783,
                            8173033, 7749105, 5797046, 759667, 8000685, 6220552, 844359, 9618981, 1360686, 46343,
                            8692923]
print(len(subjects_as_ints))

labels = ['cosine_feature', 'count_feature', 'hr_feature', 'time_feature', 'psg_label']
cosine_features = []
count_features = []
hr_features = []
time_features = []
psg_labels = []

for i in subjects_as_ints:
    subject_number = str(i)

    with open("../outputs/features/" + subject_number + "_cosine_feature.out", 'r') as file:
        for line in file:
            cosine_features.append(float(line))

    with open("../outputs/features/" + subject_number + "_count_feature.out", 'r') as file:
        for line in file:
            count_features.append(float(line))

    with open("../outputs/features/" + subject_number + "_hr_feature.out", 'r') as file:
        for line in file:
            hr_features.append(float(line))
            
    with open("../outputs/features/" + subject_number + "_time_feature.out", 'r') as file:
        for line in file:
            time_features.append(float(line))

    with open("../outputs/features/" + subject_number + "_psg_labels.out", 'r') as file:
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
    newArray.append(hr_features[index])
    newArray.append(time_features[index])
    newArray.append(psg_labels[index])

    data.append(newArray)

with open('data/bigboy.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(data)



