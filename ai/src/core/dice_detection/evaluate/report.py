from src.backend.logging import logger
from src.backend import yaml

import numpy as np

def report(
    all_ciou_scores: list,
    correct_detections: int,
    total_predictions: int,
    total_gts: int,
    inference_times: list,
    model_basename: str,
    output_pathbase: str
):

    mean_ciou = float(np.mean(all_ciou_scores)) if all_ciou_scores else 0.0
    precision = correct_detections / total_predictions if total_predictions > 0 else 0.0
    recall = correct_detections / total_gts if total_gts > 0 else 0.0
    # Calculate average inference time using only the last 10 records
    last_n_inference_times = inference_times[-10:] if len(inference_times) >= 10 else inference_times
    avg_sample_inference_ms = float((np.mean(last_n_inference_times) * 1000) if last_n_inference_times else 0)
    metrics = {
        "model": model_basename,
        "mean_ciou": mean_ciou,
        "precision": precision,
        "recall": recall,
        "correct_detections": correct_detections,
        "total_predictions": total_predictions,
        "total_gts": total_gts,
        "avg_sample_inference_ms": avg_sample_inference_ms,
    }

    # Write metrics to YAML
    filepath = f"{output_pathbase}.yml"
    with open(filepath, 'w') as f:
        yaml.dump(metrics, f, default_flow_style=False)
    logger.info(f"Evaluation metrics saved to {filepath}")