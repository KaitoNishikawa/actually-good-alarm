import os
import joblib
import numpy as np
from tensorflow.keras.models import load_model

# This script shows how to load and use the trained models for prediction on new data.

# --- 1. Define Paths and Load Models ---

# Directory where models and the scaler are saved
models_dir = "saved_models"
postprocessing_models_dir = os.path.join("postprocessing", models_dir)
# postprocessing_models_dir = "saved_models"


# Check if the models directory exists
if not os.path.exists(postprocessing_models_dir):
    print(f"Error: Models directory not found at '{postprocessing_models_dir}'")
    print("Please run the 'create_model_frfr.ipynb' notebook first to train and save the models.")
else:
    # Load the scikit-learn (Random Forest) model
    rf_model_path = os.path.join(postprocessing_models_dir, "Random_Forest.joblib")
    loaded_rf_model = joblib.load(rf_model_path)
    print(f"Successfully loaded Random Forest model from {rf_model_path}")

    # Load the TensorFlow/Keras model
    tf_model_path = os.path.join(postprocessing_models_dir, "tensorflow_model.h5")
    loaded_tf_model = load_model(tf_model_path)
    print(f"Successfully loaded TensorFlow model from {tf_model_path}")

    # Load the scaler
    scaler_path = os.path.join(postprocessing_models_dir, "scaler.joblib")
    loaded_scaler = joblib.load(scaler_path)
    print(f"Successfully loaded scaler from {scaler_path}")


    # --- 2. Prepare New Data for Prediction ---

    # Example new data with 4 features: ['cosine_feature', 'count_feature', 'hr_feature', 'time_feature']
    # This is where you would input your new, unseen data.
    new_data = np.array([
        [0.8, 25, 80, 1630002000],  # Sample data point 1
        [-0.5, 2, 55, 1630008000]   # Sample data point 2
    ])

    print("\nUsing sample data for prediction:")
    print(new_data)


    # --- 3. Make Predictions ---

    # a) Prediction with the scikit-learn (Random Forest) model
    # This model does not require scaling based on the notebook setup.
    rf_predictions = loaded_rf_model.predict(new_data)
    print("\nPredictions from Random Forest model:")
    print(rf_predictions)

    # b) Prediction with the TensorFlow model
    # This model requires the data to be scaled using the same scaler used for training.
    new_data_scaled = loaded_scaler.transform(new_data)
    
    # The output will be probabilities for each class.
    # We can use np.argmax to get the predicted class index.
    tf_predictions_probabilities = loaded_tf_model.predict(new_data_scaled)
    tf_predictions = np.argmax(tf_predictions_probabilities, axis=1)

    print("\nPredictions from TensorFlow model:")
    print(tf_predictions)
    print("\nProbabilities from TensorFlow model:")
    print(tf_predictions_probabilities)
