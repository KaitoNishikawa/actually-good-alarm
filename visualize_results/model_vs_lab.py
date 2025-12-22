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
MODELS_DIR = PROJECT_ROOT.joinpath("postprocessing", "saved_models")

FEATURE_FILES: Dict[str, str] = {
    "cosine_feature": "cosine_feature",
    "count_feature": "count_feature",
    "hr_feature": "hr_feature",
    "time_feature": "time_feature",
}

SUBJECT_IDS: Sequence[str] = ("9106476", "9618981", "9961348")
STAGE_NAMES = {
    0: "Wake",
    1: "N1",
    2: "N2",
    3: "N3",
    4: "REM",
}
DEFAULT_SUBJECT: Optional[str] = None
SCALER_FILENAME = "scaler.joblib"
SUPPORTED_MODEL_SUFFIXES = {".joblib", ".h5"}
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
    scaler_path = MODELS_DIR / SCALER_FILENAME
    if not scaler_path.exists():
        raise FileNotFoundError(
            "TensorFlow model requires a scaler, but 'postprocessing/saved_models/scaler.joblib' is missing."
        )
    return joblib.load(scaler_path)


def _load_tensorflow_model(model_path: Path):
    try:
        from tensorflow.keras.models import load_model
    except ImportError as exc:
        raise ImportError("TensorFlow must be installed to evaluate .h5 models.") from exc

    return load_model(model_path)


def _predict_with_model(model_path: Path, features: np.ndarray) -> np.ndarray:
    if model_path.suffix == ".joblib":
        model = joblib.load(model_path)
        return model.predict(features)

    if model_path.suffix == ".h5":
        scaler = _load_scaler()
        scaled_features = scaler.transform(features).astype(np.float32)
        tf_model = _load_tensorflow_model(model_path)
        probabilities = tf_model.predict(scaled_features, verbose=0)
        return np.argmax(probabilities, axis=1)

    raise ValueError(
        f"Unsupported model suffix '{model_path.suffix}'. Supported: {sorted(SUPPORTED_MODEL_SUFFIXES)}"
    )


def _prepare_subject_arrays(subject_id: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    series: Dict[str, np.ndarray] = {}

    for column, suffix in FEATURE_FILES.items():
        feature_values = _read_series(FEATURE_DIR / f"{subject_id}_{suffix}.out")
        series[column] = np.asarray(feature_values, dtype=float)

    raw_labels = np.asarray(
        [int(round(value)) for value in _read_series(FEATURE_DIR / f"{subject_id}_psg_labels.out")],
        dtype=int,
    )
    raw_labels = np.where(raw_labels == 4, 3, raw_labels)

    lengths = {len(arr) for arr in series.values()}
    lengths.add(len(raw_labels))
    if len(lengths) != 1:
        raise ValueError(f"Mismatched lengths found for subject {subject_id}: {lengths}")

    feature_matrix = np.column_stack(
        [series["cosine_feature"], series["count_feature"], series["hr_feature"], series["time_feature"]]
    )
    time_axis = series["time_feature"].copy()

    return feature_matrix, raw_labels, time_axis


def _labels_to_model_space(raw_labels: np.ndarray) -> np.ndarray:
    processed = np.where(raw_labels == 4, 3, raw_labels)
    processed = np.where(processed == 5, 4, processed)
    return processed.astype(int)


def _predictions_to_label_space(predictions: np.ndarray) -> np.ndarray:
    return np.where(predictions == 4, 5, predictions).astype(int)


def _save_predictions(subject_id: str, model_name: str, predictions: np.ndarray) -> Path:
    MODEL_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    sanitized_model = model_name.replace(" ", "_")
    output_path = MODEL_RESULTS_DIR / f"{subject_id}_{sanitized_model}_model_results.txt"

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
    ax.plot(time_axis, true_labels, color="tab:blue", linewidth=1, label="PSG Labels")
    ax.plot(
        time_axis,
        predictions,
        color="tab:orange",
        linewidth=1,
        linestyle=":",
        label="Model Predictions",
    )
    ax.set_title(f"Subject {subject_id} – {model_name}")
    ax.set_ylabel("Sleep Stage")
    ax.set_xlabel("Time Feature")
    ax.legend()
    fig.tight_layout()
    plt.show()
    plt.close(fig)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Load outputs_lab features for a subject, run the saved model, and plot predictions vs PSG labels."
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
            "Specific model filename inside postprocessing/saved_models. "
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


def main() -> None:
    args = _parse_args()

    subject_ids = [args.subject] if args.subject else list(SUBJECT_IDS)
    model_paths = _collect_model_paths(args.model)

    model_mean_precisions: List[Tuple[str, np.ndarray]] = []

    for model_path in model_paths:
        model_name = model_path.stem
        print("\n==============================")
        print(f"Evaluating model file: {model_path.name}")

        subject_precisions: List[np.ndarray] = []
        plot_payloads: List[Tuple[str, np.ndarray, np.ndarray, np.ndarray]] = []

        for subject_id in subject_ids:
            features, raw_labels, time_axis = _prepare_subject_arrays(subject_id)
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
            subject_precisions.append(precision_vector)

            print(f"Subject {subject_id} – precision by stage:")
            for stage, precision in enumerate(precision_vector):
                print(f"  Stage {stage} ({STAGE_NAMES[stage]}): {precision:.4f}")
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
            model_mean_precisions.append((model_name, mean_precisions))
        else:
            mean_precisions = None

        for subject_id, time_axis, raw_labels, predictions_raw_space in plot_payloads:
            _plot_predictions(subject_id, model_name, time_axis, raw_labels, predictions_raw_space)
            print(f"  Figure rendered on screen for subject {subject_id} (not saved)")

    if model_mean_precisions:
        print("\n==============================")
        print("Average precision across subjects (all models):")
        for model_name, mean_precisions in model_mean_precisions:
            print(f"\n{model_name}:")
            for stage, precision in enumerate(mean_precisions):
                print(f"  Stage {stage} ({STAGE_NAMES[stage]}): {precision:.4f}")
    

if __name__ == "__main__":
    main()