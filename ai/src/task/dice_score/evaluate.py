import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from tqdm import tqdm
import time
from src.dataset import S7DatasetDiceScore, get_dice_crops

from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score
import os
import yaml
from src.backend.logging import logger
from src.config.config import ParsedConfig
from src.model.utils.determ import enable_determ
from src.task.dice_score.inference import DiceScoreInference
from src.dataset.dice_score.tf import make_tf_dataset


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
    model_extension = (
        ext[1:] if ext else "keras"
    )  # Remove leading dot, default to keras
    is_tflite = model_extension == "tflite"

    inference = None

    if is_tflite:
        # Load TFLite model
        inference = DiceScoreInference(
            model_path=model_path,
            image_resolution=task.image_resolution,
            colored=config.colored,
        )
        logger.info(f"Loaded TFLite model from {model_path}")
    else:
        # Load Keras model
        model = tf.keras.models.load_model(model_path)
        logger.info(f"Loaded Keras model from {model_path}")

        @tf.function(reduce_retracing=True)
        def keras_infer_step(input_tensor):
            return model(input_tensor, training=False)

    # Get validation dataset
    logger.info("Loading validation dataset...")
    val_dataset_obj, val_dataset = get_val_dataset(config, task)

    # Calculate precision, recall, and F1 score on validation set
    # Get model name from path
    model_name_base = os.path.splitext(os.path.basename(model_path))[0]
    model_name = f"{model_name_base}-{model_extension}"
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
            if is_tflite and inference:
                # Use TFLite inference for each image
                batch_preds = []
                batch_inference_time = 0.0
                for img_idx, img in enumerate(batch_images):
                    start_time = time.perf_counter()
                    pred = inference(img)
                    end_time = time.perf_counter()
                    elapsed = end_time - start_time
                    inference_times.append(elapsed)
                    batch_inference_time += elapsed
                    predicted = pred - 1  # Convert 1-6 to 0-5 for evaluation
                    batch_preds.append(predicted)

                    # Capture for visualization after inference
                    if viz_data["img_count"] < 8:
                        img_display = (img.numpy() * 255).astype(np.uint8)
                        viz_images.append(
                            {
                                "img": img_display,
                                "actual": int(batch_labels[img_idx]),
                                "predicted": predicted,
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
                pred_labels = np.array(batch_preds)
            else:
                # Use Keras model - inference one by one
                batch_preds = []
                batch_inference_time = 0.0
                for img_idx, img in enumerate(batch_images):
                    start_time = time.perf_counter()
                    pred = keras_infer_step(img[None, ...])
                    end_time = time.perf_counter()
                    elapsed = end_time - start_time
                    inference_times.append(elapsed)
                    batch_inference_time += elapsed
                    predicted = int(tf.argmax(pred[0]).numpy())
                    batch_preds.append(predicted)

                    # Capture for visualization after inference
                    if viz_data["img_count"] < 8:
                        img_display = (img.numpy() * 255).astype(np.uint8)
                        viz_images.append(
                            {
                                "img": img_display,
                                "actual": int(batch_labels[img_idx]),
                                "predicted": predicted,
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
                pred_labels = np.array(batch_preds)

            all_true_labels.extend(np.asarray(batch_labels))
            all_predictions.extend(pred_labels)

    all_true_labels = np.array(all_true_labels)
    all_predictions = np.array(all_predictions)

    precision = precision_score(
        all_true_labels, all_predictions, average="weighted", zero_division=0
    )
    recall = recall_score(
        all_true_labels, all_predictions, average="weighted", zero_division=0
    )
    f1 = f1_score(all_true_labels, all_predictions, average="weighted", zero_division=0)

    # Generate visualization of first 8 images
    if output_dir and model_name and len(viz_images) > 0:
        rows, cols = 4, 2
        fig, axes = plt.subplots(rows, cols, figsize=(12, 16), dpi=80)
        axes = axes.flatten()

        for idx, data in enumerate(viz_images):
            ax = axes[idx]
            ax.imshow(
                data["img"].squeeze(),
                cmap="gray" if data["img"].shape[-1] == 1 else None,
            )

            # Add text overlay with predicted and actual values
            pred_text = f"Pred: {data['predicted']}"
            actual_text = f"Actual: {data['actual']}"
            color = "green" if data["predicted"] == data["actual"] else "red"

            ax.text(
                0.05,
                0.95,
                pred_text,
                transform=ax.transAxes,
                fontsize=12,
                color=color,
                fontweight="bold",
                verticalalignment="top",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
            )
            ax.text(
                0.05,
                0.05,
                actual_text,
                transform=ax.transAxes,
                fontsize=12,
                color="blue",
                fontweight="bold",
                verticalalignment="bottom",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
            )

            ax.set_title(f"Image {idx + 1}", fontsize=12, fontweight="bold")
            ax.axis("off")

        # Hide unused subplots
        for i in range(len(viz_images), rows * cols):
            axes[i].axis("off")

        # Add legend
        legend_elements = [
            Rectangle(
                (0, 0),
                1,
                1,
                facecolor="white",
                edgecolor="green",
                label="Correct Prediction",
            ),
            Rectangle(
                (0, 0),
                1,
                1,
                facecolor="white",
                edgecolor="red",
                label="Wrong Prediction",
            ),
        ]
        fig.legend(
            handles=legend_elements,
            loc="upper center",
            bbox_to_anchor=(0.5, 0.98),
            ncol=2,
            fontsize=12,
        )

        # Save visualization
        viz_path = os.path.join(output_dir, "eval.png")
        plt.tight_layout()
        plt.savefig(viz_path, dpi=300, bbox_inches="tight")
        plt.close()
        logger.info(f"Predictions visualization saved to {viz_path}")

    # Create metrics dict
    avg_inference_time = np.mean(inference_times) if inference_times else 0.0
    metrics = {
        "model": model_name_base,
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "val_samples": len(all_true_labels),
        "model_type": model_extension,
        "avg_inference_time": float(avg_inference_time),
    }

    # Write metrics to YAML
    yml_path = os.path.join(output_dir, "eval.yml")
    with open(yml_path, "w") as f:
        yaml.dump(metrics, f, default_flow_style=False)
    logger.info(f"Evaluation metrics saved to {yml_path}")
