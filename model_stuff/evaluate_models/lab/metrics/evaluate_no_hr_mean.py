import pandas as pd
import os
import joblib
from sklearn.metrics import classification_report

df = pd.read_csv("model_stuff/data/test/bigboy_no_hr_mean.csv")
x = df[['cosine_feature', 'count_feature', 'hr_std', 'time_feature']]
y = df['psg_label']

y.replace({5: 4}, inplace=True)

models_dir = "model_stuff/saved_models/no_hr_mean"

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