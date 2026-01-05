import pandas as pd
import numpy as np
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
    df.to_csv(f"model_stuff/data/test/individual/hella_features_new_time_window/{subject_number}.csv", index=False)

bigboy_df = pd.concat(data, ignore_index=True)
bigboy_df.to_csv("model_stuff/data/test/bigboy_hella_features_new_time_window.csv", index=False)





