import tensorflow as tf
import numpy as np
from tqdm import tqdm
import time
from src.dataset import S7DatasetDiceScore, get_dice_crops

from sklearn.model_selection import train_test_split
from src.task.shared.clsfi import calc_clsfi_metrics
import os
import yaml
from src.backend.logging import logger
from src.config.config import ParsedConfig
from src.model.utils.determ import enable_determ
from src.task.dice_score.inference import DotKerasInference, DotTfliteInference
from src.dataset.dice_score.tf import make_tf_dataset
from src.task.dice_score.plot import plot_evaluation_results

def get_val_dataset(config: ParsedConfig, task: ParsedConfig.Tasks.DiceScore):
    # Prepare validation dataset
    all_dice_crops = get_dice_crops(
        dataset_path=config.dataset_path,
        num_workers=config.num_workers,
    )

    # Split into train and validation (using same split as training)
    enable_determ()
    _, val_crops = train_test_split(all_dice_crops, test_size=0.3, random_state=42)

    val_dataset_obj = S7DatasetDiceScore(
        image_resolution=task.image_resolution,
        dice_crops=val_crops,
        colored=config.colored,
        num_workers=4,
        use_random=False,
        dataset_repeat=task.val_dataset_repeat,
        cache_path="output/dice_score_eval",
    )

    val_dataset = make_tf_dataset(
        val_dataset_obj,
        batch_size=1,
        image_resolution=task.image_resolution,
        colored=config.colored,
        use_random=config.use_random,
    )

    return val_dataset_obj, val_dataset


def evaluate_model(model_path: str, config, task):
    # Get model extension
    _, ext = os.path.splitext(model_path)
    ext = (
        ext[1:] if ext else "keras"
    )  # Remove leading dot, default to keras
    if ext == "tflite":
        evaluator = DotTfliteInference(
            model_path=model_path
        )
    else:
        evaluator = DotKerasInference(
            model_path=model_path,
        )

    # Get validation dataset
    logger.info("Loading validation dataset...")
    val_dataset_obj, val_dataset = get_val_dataset(config, task)

    # Calculate precision, recall, and F1 score on validation set
    # Get model name from path
    model_name_base = os.path.splitext(os.path.basename(model_path))[0]
    output_dir = os.path.dirname(model_path)

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
                pred = evaluator(img)
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
        path_base=f"{output_dir}/eval-{ext}", 
        viz_images=viz_images)

    # Create metrics dict
    avg_inference_time = np.mean(inference_times) if inference_times else 0.0

    precision, recall, f1 = calc_clsfi_metrics(
        targets=np.array(all_true_labels),
        preds=np.array(all_predictions)
    )

    metrics = {
        "model": model_name_base,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "model_type": ext,
        "avg_inference_time": float(avg_inference_time),
    }

    # Write metrics to YAML
    yml_path = f"{output_dir}/eval-{ext}.yml"
    with open(yml_path, "w") as f:
        yaml.dump(metrics, f, default_flow_style=False)
    logger.info(f"Evaluation metrics saved to {yml_path}")
