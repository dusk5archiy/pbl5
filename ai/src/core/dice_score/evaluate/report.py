from src.functions.clsfi import calc_clsfi_metrics
from src.backend import yaml
from src.backend.logging import logger

import numpy as np


def report(
    inference_times,
    all_true_labels,
    all_predictions,
    model_name_base: str,
    output_pathbase: str,
):
    avg_inference_time = np.mean(inference_times) if inference_times else 0.0

    precision, recall, f1 = calc_clsfi_metrics(
        targets=np.array(all_true_labels), preds=np.array(all_predictions)
    )

    metrics = {
        "model": model_name_base,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "avg_inference_time": float(avg_inference_time),
    }

    # Write metrics to YAML
    yml_path = f"{output_pathbase}.yml"
    with open(yml_path, "w") as f:
        yaml.dump(metrics, f, default_flow_style=False)
    logger.info(f"Evaluation metrics saved to {yml_path}")
