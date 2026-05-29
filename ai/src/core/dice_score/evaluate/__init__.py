from .dataset import load_dataset
from .plot import plot_confusion_matrix, plot_evaluation_results
from .report import report

from src.backend.logging import logger
from src.config import ParsedConfig
from src.core.dice_score.inference import DiceScoreInference
from src.utils.file import split_path

from tqdm import tqdm

import numpy as np
import tensorflow as tf
import os
import time

# Suppress internal TensorFlow rendezvous info logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

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
    logger.info("Loading validation dataset for timing (Batch 1)...")
    val_dataset_obj, time_dataset = load_dataset(config, task, batch_size=1)

    logger.info("Calculating metrics on validation set...")
    all_true_labels = []
    all_predictions = []
    inference_times = []  # Store inference times for average calculation

    # 1. Measurement of average inference time (10 samples)
    logger.info("Measuring inference time (10 samples)...")
    time_samples_count = 0
    total_samples_for_time = 10

    for batch_images, _ in time_dataset:
        for img in batch_images:
            start_time = time.perf_counter()
            _ = inference.model(img)
            end_time = time.perf_counter()
            inference_times.append(end_time - start_time)
            time_samples_count += 1
            if time_samples_count >= total_samples_for_time:
                break
        if time_samples_count >= total_samples_for_time:
            break

    avg_inf_ms = (sum(inference_times) / len(inference_times)) * 1000
    logger.info(f"Average inference time: {avg_inf_ms:.2f} ms")

    # 2. Measurement of accuracy (Full dataset with Batch 8)
    logger.info("Loading validation dataset for accuracy (Batch 8)...")
    val_dataset_obj, val_dataset = load_dataset(config, task, batch_size=8)
    
    # Calculate exactly how many samples are in the test set
    total_samples = len(val_dataset_obj)
    train_count = int(total_samples * 0.70)
    val_count = int(total_samples * 0.15)
    test_count = total_samples - train_count - val_count

    logger.info("Calculating accuracy on full validation set...")
    # For visualization: store first 8 images
    viz_images = []
    viz_data = {"img_count": 0}

    with tqdm(total=test_count, desc="Accuracy Eval", unit="sample") as pbar:
        try:
            for batch_images, batch_labels in val_dataset:
                for (img, lbl) in zip(batch_images, batch_labels):
                    lbl = int(lbl)
                    pred = inference.model(img)

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

                    pbar.update(1)
        except (tf.errors.OutOfRangeError, StopIteration):
            logger.info("End of dataset reached (OutOfRange).")

    plot_evaluation_results(
        output_pathbase=output_pathbase, 
        viz_images=viz_images)

    plot_confusion_matrix(
        output_pathbase=output_pathbase,
        all_true_labels=all_true_labels,
        all_predictions=all_predictions,
    )

    # Create metrics dict
    report(
        inference_times=inference_times,
        all_true_labels=all_true_labels,
        all_predictions=all_predictions,
        model_name_base=model_basename,
        output_pathbase=output_pathbase
    )
