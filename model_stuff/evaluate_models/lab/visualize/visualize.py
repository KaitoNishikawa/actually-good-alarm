import pandas as pd
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report

subjects_as_ints = [
    9106476, 9618981, 9961348
]

test_sets = {}

for i in subjects_as_ints:
    df = pd.read_csv(f"model_stuff/data/test/individual/hella_features/{i}.csv")
    # x = df[['cosine_feature', 'count_feature', 'hr_std', 'hr_mean', 'time_feature', 'hr_mean_diff']]
    x = df[['cosine_feature', 'count_feature', 'hr_std', 'hr_mean', 'time_feature', 
        'count_feature_lag_1', 'count_feature_lag_2', 'hr_std_lag_1', 'hr_std_lag_2', 
        'hr_mean_lag_1', 'hr_mean_lag_2', 'hr_mean_delta'
    ]]
    y = df['psg_label']

    y.replace({5: 4}, inplace=True)

    test_sets[i] = [x, y]

models_dir = "model_stuff/saved_models/hella_features/Random_Forest.joblib"
clf = joblib.load(models_dir)

for subject_id, (x, y) in test_sets.items():
    y_pred = clf.predict(x)
    report = classification_report(y, y_pred)
    
    plt.figure(figsize=(15, 8))
    
    # Plot the labels
    plt.subplot(2, 1, 1)
    plt.plot(y.values, label='True Labels', alpha=0.7, linewidth=2)
    plt.plot(y_pred, label='Predicted Labels', alpha=0.7, linestyle='--', linewidth=2)
    plt.title(f"Subject {subject_id} - Random Forest")
    plt.xlabel("Time (epochs)")
    plt.ylabel("Sleep Stage")
    plt.legend()
    plt.yticks([0, 1, 2, 3, 4], ['Wake', 'N1', 'N2', 'N3', 'REM'])
    
    # Display classification report as text
    plt.subplot(2, 1, 2)
    plt.axis('off')
    plt.text(0.05, 0.95, report, family='monospace', fontsize=10, verticalalignment='top')
    
    plt.tight_layout()
    plt.show()