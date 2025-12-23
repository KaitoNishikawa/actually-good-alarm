import os
import joblib
import numpy as np
from tensorflow.keras.models import load_model

class Model:
    def run_model(data, file_number_as_str):
        models_dir = "model_stuff/saved_models/hella_features"

        if not os.path.exists(models_dir):
            print(f"Models directory not found at '{models_dir}'")
            print("Run notebook first to train and save the models.")
        else:
            rf_model_path = os.path.join(models_dir, "Random_Forest.joblib")
            loaded_rf_model = joblib.load(rf_model_path)

        rf_predictions = loaded_rf_model.predict(data)
        rf_predictions = np.where(rf_predictions == 4, 5, rf_predictions)

        with open('model_stuff/model_results/' + file_number_as_str + '_model_results.txt', 'w') as file:
            for index, i in enumerate(rf_predictions):
                line = str(rf_predictions[index]) + '\n'
                file.write(line)
        
        return rf_predictions        