import argparse
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import joblib
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import classification_report

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FEATURE_DIR = PROJECT_ROOT.joinpath("outputs_lab", "features")
MODEL_RESULTS_DIR = PROJECT_ROOT.joinpath("model_results")
# Pointing to the directory where optimized models were saved
MODELS_DIR = PROJECT_ROOT.joinpath("postprocessing", "saved_models_optimized")

FEATURE_FILES: Dict[str, str] = {
    "cosine_feature": "cosine_feature",
    "count_feature": "count_feature",
    "time_feature": "time_feature",
}
HR_FEATURE_SUFFIX = "hr_feature"

SUBJECT_IDS: Sequence[str] = ("9106476", "9618981", "9961348")
STAGE_NAMES = {
    0: "Wake",
    1: "N1",
    2: "N2",
    3: "N3",
    4: "REM",
}
DEFAULT_SUBJECT: Optional[str] = None
SCALER_FILENAME = "scaler.joblib" # Scaler might not be in the optimized dir, or might be named differently.
# The notebook didn't explicitly save a scaler in the last step, but the models might include the pipeline or expect raw features.
# The notebook trained on: x = df[['cosine_feature', 'count_feature', 'hr_feature', 'time_feature']]
# It didn't seem to use a scaler in the pipeline for tree models, but maybe for MLP/LR.
# If MLP was saved, it expects scaled data if it was trained on scaled data.
# Looking at the notebook, there was `from sklearn.preprocessing import StandardScaler` but I didn't see it applied to x_train/x_test in the snippet I read.
# Wait, the snippet showed:
# x = df[['cosine_feature', 'count_feature', 'hr_feature', 'time_feature']]
# x_train, x_test, y_train, y_test = train_test_split(x, y, ...)
# So no scaling was applied before splitting.
# Tree models don't need scaling. MLP/LR do.
# If MLP was trained on unscaled data, it might perform poorly, but that's how it was trained in the notebook snippet I saw.
# So I will assume no scaler is needed for now, or that the model handles it.

SUPPORTED_MODEL_SUFFIXES = {".joblib", ".h5", ".pkl"}
SKIP_MODEL_BASENAMES = {SCALER_FILENAME}
SKIP_MODEL_BASENAMES_LOWER = {name.lower() for name in SKIP_MODEL_BASENAMES}


def _read_series(file_path: Path) -> List[float]:
    if not file_path.exists():
        raise FileNotFoundError(f"Missing input file: {file_path}")

    with file_path.open("r", encoding="utf-8") as handle:
        return [float(line.strip()) for line in handle if line.strip()]


def _collect_model_paths(selected_model: Optional[str]) -> List[Path]:
    if selected_model:
        candidate = MODELS_DIR / selected_model
        if not candidate.exists():
            raise FileNotFoundError(f"Model not found at {candidate}")
        if candidate.name.lower() in SKIP_MODEL_BASENAMES_LOWER:
            raise ValueError(f"Selected file {selected_model} is not a trainable model artifact.")
        if candidate.suffix not in SUPPORTED_MODEL_SUFFIXES:
            raise ValueError(
                f"Unsupported model suffix '{candidate.suffix}'. Supported: {sorted(SUPPORTED_MODEL_SUFFIXES)}"
            )
        return [candidate]

    if not MODELS_DIR.exists():
        raise FileNotFoundError(f"Models directory not found at '{MODELS_DIR}'")

    discovered = sorted(
        path
        for path in MODELS_DIR.iterdir()
        if path.is_file()
        and path.suffix in SUPPORTED_MODEL_SUFFIXES
        and path.name.lower() not in SKIP_MODEL_BASENAMES_LOWER
    )

    if not discovered:
        raise FileNotFoundError(
            f"No supported models found in '{MODELS_DIR}'. Expected suffixes: {sorted(SUPPORTED_MODEL_SUFFIXES)}"
        )

    return discovered


def _load_scaler():
    # Try to find scaler in the optimized dir, or fallback to the main saved_models dir
    scaler_path = MODELS_DIR / SCALER_FILENAME
    if not scaler_path.exists():
        scaler_path = PROJECT_ROOT.joinpath("postprocessing", "saved_models", SCALER_FILENAME)
    
    if not scaler_path.exists():
        # If no scaler found, return None. The prediction function will handle it.
        return None
    return joblib.load(scaler_path)


def _load_tensorflow_model(model_path: Path):
    try:
        from tensorflow.keras.models import load_model
    except ImportError as exc:
        raise ImportError("TensorFlow must be installed to evaluate .h5 models.") from exc

    return load_model(model_path)


def _predict_with_model(model_path: Path, features: np.ndarray) -> np.ndarray:
    if model_path.suffix in {".joblib", ".pkl"}:
        model = joblib.load(model_path)
        return model.predict(features)

    if model_path.suffix == ".h5":
        scaler = _load_scaler()
        if scaler:
            scaled_features = scaler.transform(features).astype(np.float32)
        else:
            # Fallback to raw features if no scaler found (warning: might be wrong for NN)
            print("Warning: No scaler found for .h5 model. Using raw features.")
            scaled_features = features.astype(np.float32)
            
        tf_model = _load_tensorflow_model(model_path)
        probabilities = tf_model.predict(scaled_features, verbose=0)
        return np.argmax(probabilities, axis=1)

    raise ValueError(
        f"Unsupported model suffix '{model_path.suffix}'. Supported: {sorted(SUPPORTED_MODEL_SUFFIXES)}"
    )


def _read_hr_stats(file_path: Path) -> Tuple[np.ndarray, np.ndarray]:
    if not file_path.exists():
        raise FileNotFoundError(f"Missing input file: {file_path}")

    std_values: List[float] = []
    mean_values: List[float] = []

    with file_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue

            parts = stripped.split()
            std_values.append(float(parts[0]))
            if len(parts) >= 2:
                mean_values.append(float(parts[1]))
            else:
                # Fallback: if historical files only had one column, reuse it for mean
                mean_values.append(float(parts[0]))

    if not std_values:
        raise ValueError(f"No heart rate statistics found in {file_path}")

    return np.asarray(std_values, dtype=float), np.asarray(mean_values, dtype=float)


def _prepare_subject_arrays(subject_id: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    series: Dict[str, np.ndarray] = {}

    for column, suffix in FEATURE_FILES.items():
        feature_values = _read_series(FEATURE_DIR / f"{subject_id}_{suffix}.out")
        series[column] = np.asarray(feature_values, dtype=float)

    hr_std_values, hr_mean_values = _read_hr_stats(FEATURE_DIR / f"{subject_id}_{HR_FEATURE_SUFFIX}.out")
    series["hr_std_feature"] = hr_std_values
    series["hr_mean_feature"] = hr_mean_values

    raw_labels = np.asarray(
        [int(round(value)) for value in _read_series(FEATURE_DIR / f"{subject_id}_psg_labels.out")],
        dtype=int,
    )
    # Map 4 (Deep) to 3, because our models are trained 0-4 where 3 is Deep and 4 is REM?
    # Wait, in the notebook:
    # y.replace({5: 4}, inplace=True)
    # So 0=Wake, 1=N1, 2=N2, 3=N3/Deep, 4=REM.
    # The lab data might have 0=Wake, 1=N1, 2=N2, 3=N3, 4=N4(Deep?), 5=REM?
    # The original script did: raw_labels = np.where(raw_labels == 4, 3, raw_labels)
    # This implies 4 in raw data is Deep Sleep (N4), which is merged into N3 (3).
    # And then _labels_to_model_space did:
    # processed = np.where(raw_labels == 4, 3, raw_labels)
    # processed = np.where(processed == 5, 4, processed)
    # This maps 5 (REM) to 4.
    
    # Let's keep the logic consistent with the original script.
    raw_labels = np.where(raw_labels == 4, 3, raw_labels)

    lengths = {len(arr) for arr in series.values()}
    lengths.add(len(raw_labels))
    if len(lengths) != 1:
        raise ValueError(f"Mismatched lengths found for subject {subject_id}: {lengths}")

    feature_matrix = np.column_stack(
        [
            series["cosine_feature"],
            series["count_feature"],
            series["hr_std_feature"],
            series["hr_mean_feature"],
            series["time_feature"],
        ]
    )
    time_axis = series["time_feature"].copy()

    return feature_matrix, raw_labels, time_axis


def _labels_to_model_space(raw_labels: np.ndarray) -> np.ndarray:
    # Original script logic:
    # processed = np.where(raw_labels == 4, 3, raw_labels) # 4->3
    # processed = np.where(processed == 5, 4, processed) # 5->4
    
    # Since we already did 4->3 in _prepare_subject_arrays, we just need to handle 5->4 here if it wasn't done.
    # But wait, _prepare_subject_arrays returns raw_labels with 4->3 already applied.
    # So raw_labels has 0, 1, 2, 3, 5.
    # We need to map 5 to 4.
    processed = np.where(raw_labels == 5, 4, raw_labels)
    return processed.astype(int)


def _predictions_to_label_space(predictions: np.ndarray) -> np.ndarray:
    # Model outputs 0-4.
    # We want to map back to "raw" space for plotting/saving?
    # Original script: return np.where(predictions == 4, 5, predictions).astype(int)
    # This maps 4 (REM) back to 5.
    return np.where(predictions == 4, 5, predictions).astype(int)


def _save_predictions(subject_id: str, model_name: str, predictions: np.ndarray) -> Path:
    MODEL_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    sanitized_model = model_name.replace(" ", "_")
    output_path = MODEL_RESULTS_DIR / f"{subject_id}_{sanitized_model}_optimized_results.txt"

    with output_path.open("w", encoding="utf-8") as handle:
        for value in predictions:
            handle.write(f"{int(value)}\n")

    return output_path


def _plot_predictions(
    subject_id: str,
    model_name: str,
    time_axis: np.ndarray,
    true_labels: np.ndarray,
    predictions: np.ndarray,
) -> None:
    fig, ax = plt.subplots(figsize=(14, 4))
    # Map true labels 5->4 for plotting consistency if needed, or just plot as is.
    # If we plot raw labels (0,1,2,3,5) and predictions (0,1,2,3,5), it should be fine.
    
    ax.plot(time_axis, true_labels, color="tab:blue", linewidth=1, label="PSG Labels")
    ax.plot(
        time_axis,
        predictions,
        color="tab:orange",
        linewidth=1,
        linestyle=":",
        label="Model Predictions",
    )
    ax.set_title(f"Subject {subject_id} – {model_name} (Optimized)")
    ax.set_ylabel("Sleep Stage")
    ax.set_xlabel("Time Feature")
    ax.legend()
    fig.tight_layout()
    plt.show()
    plt.close(fig)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Load outputs_lab features for a subject, run the OPTIMIZED saved models, and plot predictions vs PSG labels."
        )
    )
    parser.add_argument(
        "--subject",
        default=DEFAULT_SUBJECT,
        help=(
            "Subject identifier (e.g., 9106476). "
            "Leave unset to evaluate default subjects: 9106476, 9618981, 9961348."
        ),
    )
    parser.add_argument(
        "--model",
        default=None,
        help=(
            "Specific model filename inside postprocessing/saved_models_optimized. "
            "Leave unset to evaluate every supported model."
        ),
    )
    return parser.parse_args()


def _precision_vector(report_dict: Dict[str, Dict[str, float]]) -> np.ndarray:
    precisions: List[float] = []
    for stage in range(5):
        stage_key = str(stage)
        precisions.append(report_dict.get(stage_key, {}).get("precision", 0.0))
    return np.asarray(precisions, dtype=float)


def _recall_vector(report_dict: Dict[str, Dict[str, float]]) -> np.ndarray:
    recalls: List[float] = []
    for stage in range(5):
        stage_key = str(stage)
        recalls.append(report_dict.get(stage_key, {}).get("recall", 0.0))
    return np.asarray(recalls, dtype=float)


def main() -> None:
    args = _parse_args()

    subject_ids = [args.subject] if args.subject else list(SUBJECT_IDS)
    try:
        model_paths = _collect_model_paths(args.model)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure you have run the optimization notebook and saved the models.")
        return

    model_mean_stats: List[Tuple[str, np.ndarray, np.ndarray]] = []

    for model_path in model_paths:
        model_name = model_path.stem
        print("\n==============================")
        print(f"Evaluating optimized model file: {model_path.name}")

        subject_precisions: List[np.ndarray] = []
        subject_recalls: List[np.ndarray] = []
        plot_payloads: List[Tuple[str, np.ndarray, np.ndarray, np.ndarray]] = []

        for subject_id in subject_ids:
            try:
                features, raw_labels, time_axis = _prepare_subject_arrays(subject_id)
            except FileNotFoundError:
                print(f"Skipping subject {subject_id}: Data not found.")
                continue
                
            labels_for_model = _labels_to_model_space(raw_labels)

            predictions_model_space = _predict_with_model(model_path, features)
            predictions_raw_space = _predictions_to_label_space(predictions_model_space)

            accuracy = float(np.mean(predictions_model_space == labels_for_model))

            report_dict = classification_report(
                labels_for_model,
                predictions_model_space,
                digits=4,
                output_dict=True,
                zero_division=0,
            )

            precision_vector = _precision_vector(report_dict)
            recall_vector = _recall_vector(report_dict)
            subject_precisions.append(precision_vector)
            subject_recalls.append(recall_vector)

            print(f"Subject {subject_id} – precision/recall by stage:")
            for stage in range(5):
                precision = precision_vector[stage]
                recall = recall_vector[stage]
                print(
                    f"  Stage {stage} ({STAGE_NAMES[stage]}): Precision={precision:.4f} | Recall={recall:.4f}"
                )
            print(f"  Samples: {len(raw_labels)}")
            print(f"  Exact accuracy (model space): {accuracy:.4f}")

            predictions_path = _save_predictions(subject_id, model_name, predictions_raw_space)
            print(f"  Predictions saved to: {predictions_path}")

            plot_payloads.append(
                (
                    subject_id,
                    time_axis,
                    raw_labels,
                    predictions_raw_space,
                )
            )

        if subject_precisions:
            mean_precisions = np.mean(subject_precisions, axis=0)
            mean_recalls = np.mean(subject_recalls, axis=0)
            model_mean_stats.append((model_name, mean_precisions, mean_recalls))
        else:
            mean_precisions = None

        # Uncomment to show plots
        for subject_id, time_axis, raw_labels, predictions_raw_space in plot_payloads:
            _plot_predictions(subject_id, model_name, time_axis, raw_labels, predictions_raw_space)
            print(f"  Figure rendered on screen for subject {subject_id} (not saved)")

    if model_mean_stats:
        print("\n==============================")
        print("Average precision/recall across subjects (all optimized models):")
        for model_name, mean_precisions, mean_recalls in model_mean_stats:
            print(f"\n{model_name}:")
            for stage in range(5):
                precision = mean_precisions[stage]
                recall = mean_recalls[stage]
                print(
                    f"  Stage {stage} ({STAGE_NAMES[stage]}): Precision={precision:.4f} | Recall={recall:.4f}"
                )
    

if __name__ == "__main__":
    main()
