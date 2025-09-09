import os
import joblib
import numpy as np
from tensorflow.keras.models import load_model

class Model:
    def run_model(data, file_number_as_str):
        models_dir = "saved_models"
        postprocessing_models_dir = os.path.join("postprocessing", models_dir)

        if not os.path.exists(postprocessing_models_dir):
            print(f"Models directory not found at '{postprocessing_models_dir}'")
            print("Run notebook first to train and save the models.")
        else:
            rf_model_path = os.path.join(postprocessing_models_dir, "Random_Forest.joblib")
            loaded_rf_model = joblib.load(rf_model_path)

        rf_predictions = loaded_rf_model.predict(data)

        with open(file_number_as_str + '_model_results.txt', 'a') as file:
            for index, i in enumerate(rf_predictions):
                # line = str(rf_predictions[index]) + ' ' + str(int(psg_labels[index])) + '\n'
                line = str(rf_predictions[index]) + '\n'
                file.write(line)
        
        return rf_predictions