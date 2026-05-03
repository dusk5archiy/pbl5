from .dataset import load_dataset
from .plot import plot_evaluation_results
from .report import report

from src.backend.logging import logger
from src.config import ParsedConfig
from src.core.dice_score.inference import DiceScoreInference
from src.utils.file import split_path

from tqdm import tqdm

import numpy as np
import os
import time

def evaluate_model(model_path: str, config: ParsedConfig, task: ParsedConfig.Tasks.DiceScore):
    # Get model extension
    output_dir, model_basename, model_ext = split_path(filepath=model_path, default_ext="keras")

    output_pathbase = f"{output_dir}/eval-{model_ext}"
    inference = DiceScoreInference(
        model_path=model_path,
        image_resolution=task.image_resolution,
        colored=config.colored,
        zero_indexed=True,
    )

    # Get validation dataset
    logger.info("Loading validation dataset...")
    val_dataset_obj, val_dataset = load_dataset(config, task)

    logger.info("Calculating metrics on validation set...")
    all_true_labels = []
    all_predictions = []
    inference_times = []  # Store inference times for average calculation

    # For visualization: store first 8 images
    viz_images = []
    viz_data = {"img_count": 0}

    processed_samples = 0
    total_inference_time = 0.0

    with tqdm(total=len(val_dataset_obj), desc="Evaluating", unit="sample") as pbar:
        for batch_images, batch_labels in val_dataset:
            for (img, lbl) in zip(batch_images, batch_labels):
                lbl = int(lbl)
                start_time = time.perf_counter()
                pred = inference.model(img)
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                inference_times.append(elapsed)

                all_predictions.append(pred)
                all_true_labels.append(lbl)

                # Capture for visualization after inference
                if viz_data["img_count"] < 8:
                    img_display = (img.numpy() * 255).astype(np.uint8)
                    viz_images.append(
                        {
                            "img": img_display,
                            "actual": lbl,
                            "predicted": pred,
                        }
                    )
                    viz_data["img_count"] += 1

                processed_samples += 1
                total_inference_time += elapsed
                avg_inference_time = (
                    total_inference_time / processed_samples
                    if processed_samples
                    else 0.0
                )
                pbar.update(1)
                pbar.set_postfix(
                    avg_inf_ms=f"{avg_inference_time * 1000:.2f}",
                    last_sample_ms=f"{elapsed * 1000:.2f}",
                )

    plot_evaluation_results(
        output_pathbase=output_pathbase, 
        viz_images=viz_images)

    # Create metrics dict
    report(
        inference_times=inference_times,
        all_true_labels=all_true_labels,
        all_predictions=all_predictions,
        model_name_base=model_basename,
        output_pathbase=output_pathbase
    )
