import pandas as pd
import os
import joblib
from sklearn.metrics import classification_report

df = pd.read_csv("model_stuff/data/test/bigboy_hella_features.csv")
# x = df[['cosine_feature', 'count_feature', 'hr_std', 'hr_mean', 'time_feature', 'hr_mean_diff']]
x = df[['cosine_feature', 'count_feature', 'hr_std', 'hr_mean', 'time_feature', 
        'hr_mean_diff', 'count_feature_lag_1', 'count_feature_lag_2', 'hr_std_lag_1', 'hr_std_lag_2', 
        'hr_mean_lag_1', 'hr_mean_lag_2', 'delta'
]]
y = df['psg_label']

y.replace({5: 4}, inplace=True)

models_dir = "model_stuff/saved_models/hella_features"

print(f"Evaluating models from: {models_dir}")
if os.path.exists(models_dir):
    for model_file in os.listdir(models_dir):
        if model_file.endswith(".joblib"):
            model_path = os.path.join(models_dir, model_file)
            model_name = model_file.replace('.joblib', '').replace('_', ' ')
            
            clf = joblib.load(model_path)
            y_pred = clf.predict(x)
            
            print(f"--- Classification Report for {model_name} ---")
            print(classification_report(y, y_pred))
else:
    print(f"Models directory not found: {models_dir}")