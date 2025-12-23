import pandas as pd
from sklearn.preprocessing import StandardScaler

subjects_as_ints = [
    9106476, 9618981, 9961348
]

print(len(subjects_as_ints))

data = []

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
    
    df = pd.DataFrame({
        'cosine_feature': cosine_features,
        'count_feature': count_features,
        'hr_std': hr_std_features,
        'hr_mean': hr_mean_features,
        'time_feature': time_features,
        'psg_label': psg_labels
    })

    # hr_mean_diff = df['hr_mean'] - df['hr_mean'].shift(1)
    # df['hr_mean_diff'] = hr_mean_diff

    df['count_feature_lag_1'] = df['count_feature'].shift(1)
    df['count_feature_lag_2'] = df['count_feature'].shift(2)

    df['hr_std_lag_1'] = df['hr_std'].shift(1)
    df['hr_std_lag_2'] = df['hr_std'].shift(2)

    df['hr_mean_lag_1'] = df['hr_mean'].shift(1)
    df['hr_mean_lag_2'] = df['hr_mean'].shift(2)

    df['hr_mean_delta'] = df['hr_mean'] - df['hr_mean'].shift(2)

    df = df.iloc[2:]

    scaler = StandardScaler()
    df['hr_mean_delta'] = scaler.fit_transform(df[['hr_mean_delta']])

    data.append(df)
    df.to_csv(f"model_stuff/data/test/individual/hella_features/{subject_number}.csv", index=False)

bigboy_df = pd.concat(data, ignore_index=True)
bigboy_df.to_csv("model_stuff/data/test/bigboy_hella_features.csv", index=False)





