import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import os
import time
from tqdm import tqdm

from sklearn.model_selection import train_test_split

from src.dataset import (
    get_image_detection_datas,
    S7DatasetDiceDetection,
)
from src.dataset.dice_detection.tf import make_tf_dataset
from src.external.yolo_v8.bounding_box.iou import compute_ciou
from src.task.dice_detection.utils import decode_dfl
from src.task.dice_detection.inference import DiceDetectionInference
import yaml
from src.backend.logging import logger
from src.config import ParsedConfig


def get_val_dataset(config, task: ParsedConfig.Tasks.DiceDetection):
    # Prepare validation dataset
    all_image_datas = get_image_detection_datas(
        dataset_path=config.dataset_path, num_workers=config.num_workers
    )

    # Split into train and validation (using same split as training)
    _, val_datas = train_test_split(all_image_datas, test_size=0.3, random_state=42)

    val_dataset_obj = S7DatasetDiceDetection(
        image_resolution=task.image_resolution,
        image_datas=val_datas,
        colored=config.colored,
        use_random=False,
        cache_path="output/dice_detection_val",
        dataset_repeat=task.val_dataset_repeat,
        num_workers=4,
    )

    val_dataset = make_tf_dataset(
        val_dataset_obj,
        batch_size=1,
        image_resolution=task.image_resolution,
        colored=config.colored,
        use_random=config.use_random
    )

    return val_dataset_obj, val_dataset
def evaluate_with_ciou(
    inference,
    model,
    val_dataset_obj,
    val_dataset,
    image_resolution: tuple[int, int],
    output_dir: str,
    model_name: str,
    is_tflite: bool,
    iou_threshold: float = 0.7,
):
    from matplotlib.patches import Rectangle
    from matplotlib.lines import Line2D

    all_ciou_scores = []
    total_predictions = total_gts = correct_detections = 0
    inference_times = []

    # For visualization: store first 8 images
    viz_images = []
    viz_data = {"img_count": 0}

    processed_samples = 0
    total_inference_time = 0.0

    if model is not None:
        @tf.function(reduce_retracing=True)
        def keras_infer_step(input_tensor):
            return model(input_tensor, training=False)

    # Iterate dataset with progress bar
    with tqdm(total=len(val_dataset_obj), desc="Evaluating", unit="sample") as pbar:
        # Iterate over batches
        for images, targets in val_dataset:
            # Iterate samples in the batch without using explicit numeric indices
            for img_tensor, gt_boxes_tensor, gt_classes_tensor in zip(
                images, targets["boxes"], targets["classes"]
            ):
                if is_tflite:
                    # Use TFLite inference
                    img = img_tensor.numpy()
                    start_time = time.perf_counter()
                    pred_boxes_filtered = inference(img)
                    end_time = time.perf_counter()
                    elapsed = end_time - start_time
                    inference_times.append(elapsed)
                    processed_samples += 1
                    total_inference_time += elapsed
                    avg_inf_time = total_inference_time / processed_samples if processed_samples else 0.0
                    pbar.update(1)
                    pbar.set_postfix(
                        avg_inf_ms=f"{avg_inf_time * 1000:.2f}",
                        last_sample_ms=f"{elapsed * 1000:.2f}",
                    )
                    pred_boxes_filtered = np.array(pred_boxes_filtered)
                    
                    # Capture for visualization after inference
                    if viz_data["img_count"] < 8:
                        img_display = (img_tensor.numpy() * 255).astype(np.uint8)
                        viz_images.append(
                            {
                                "img": img_display,
                                "gt_boxes": gt_boxes_tensor.numpy() if hasattr(gt_boxes_tensor, "numpy") else np.array(gt_boxes_tensor),
                                "pred_boxes": pred_boxes_filtered,
                            }
                        )
                        viz_data["img_count"] += 1
                    
                    # Convert from xywh to xyxy for CIoU calculation
                    if len(pred_boxes_filtered) > 0:
                        pred_boxes_filtered = np.stack([
                            pred_boxes_filtered[:, 0],  # x
                            pred_boxes_filtered[:, 0] + pred_boxes_filtered[:, 2],  # x + w
                            pred_boxes_filtered[:, 1],  # y
                            pred_boxes_filtered[:, 1] + pred_boxes_filtered[:, 3],  # y + h
                        ], axis=1).T
                else:
                    # Use Keras model via provided keras_infer_step (tf.function), operate on tensors
                    inp = tf.expand_dims(img_tensor, axis=0)
                    start_time = time.perf_counter()
                    predictions = keras_infer_step(inp)
                    end_time = time.perf_counter()
                    elapsed = end_time - start_time
                    inference_times.append(elapsed)
                    processed_samples += 1
                    total_inference_time += elapsed
                    avg_inf_time = total_inference_time / processed_samples if processed_samples else 0.0
                    pbar.update(1)
                    pbar.set_postfix(
                        avg_inf_ms=f"{avg_inf_time * 1000:.2f}",
                        last_sample_ms=f"{elapsed * 1000:.2f}",
                    )
                    # Decode predictions (keep tensors)
                    dfl_batch = predictions["boxes"][0]
                    conf_batch = predictions["classes"][0]
                    pred_boxes_xyxy = decode_dfl(dfl_batch, image_resolution)
                    pred_confs = tf.squeeze(conf_batch)
                    # Filter predicted boxes by confidence
                    mask = pred_confs > 0.5
                    pred_boxes_filtered = tf.boolean_mask(pred_boxes_xyxy, mask)
                    
                    # Capture for visualization after inference
                    if viz_data["img_count"] < 8:
                        img_display = (img_tensor.numpy() * 255).astype(np.uint8)
                        viz_images.append(
                            {
                                "img": img_display,
                                "gt_boxes": gt_boxes_tensor.numpy() if hasattr(gt_boxes_tensor, "numpy") else np.array(gt_boxes_tensor),
                                "pred_boxes": pred_boxes_filtered.numpy() if hasattr(pred_boxes_filtered, "numpy") else np.array(pred_boxes_filtered),
                            }
                        )
                        viz_data["img_count"] += 1

            # Filter GT boxes
            # Keep GT as tensors
            gt_boxes = tf.reshape(gt_boxes_tensor, (-1, 4)) if tf.rank(gt_boxes_tensor) == 1 else gt_boxes_tensor
            gt_classes = tf.reshape(gt_classes_tensor, (-1,)) if tf.rank(gt_classes_tensor) == 0 else gt_classes_tensor
            gt_boxes_filtered = tf.boolean_mask(gt_boxes, gt_classes >= 0.0)

            # Use tensor shapes
            total_predictions += int(tf.shape(pred_boxes_filtered)[0])
            total_gts += int(tf.shape(gt_boxes_filtered)[0])

            if len(pred_boxes_filtered) == 0 or len(gt_boxes_filtered) == 0:
                # No GT or no predictions — progress already updated during inference
                continue

            # Convert GT to xyxy and compute CIoU
            gt_boxes_xyxy = np.stack(
                [
                    gt_boxes_filtered[:, 0],
                    gt_boxes_filtered[:, 1],
                    gt_boxes_filtered[:, 0] + gt_boxes_filtered[:, 2],
                    gt_boxes_filtered[:, 1] + gt_boxes_filtered[:, 3],
                ],
                axis=1,
            )

            ciou_matrix = compute_ciou(
                tf.expand_dims(
                    tf.constant(pred_boxes_filtered, dtype=tf.float32), axis=1
                ),
                tf.expand_dims(tf.constant(gt_boxes_xyxy, dtype=tf.float32), axis=0),
                bounding_box_format="xyxy",
            ).numpy()

            for i in range(len(pred_boxes_filtered)):
                best_ciou = float(np.max(ciou_matrix[i, :]))
                all_ciou_scores.append(best_ciou)
                if best_ciou > iou_threshold:
                    correct_detections += 1
            # progress updated per-sample inside inference branches (like dice_score)

    # Generate visualization of first 8 images
    if output_dir and model_name and len(viz_images) > 0:
        rows, cols = 4, 2
        fig, axes = plt.subplots(rows, cols, figsize=(12, 16), dpi=80)
        axes = axes.flatten()

        for idx, data in enumerate(viz_images):
            ax = axes[idx]
            ax.imshow(data["img"].squeeze(), cmap="gray")

            # Draw GT boxes in green
            for box in data["gt_boxes"]:
                x, y, w, h = box
                rect = Rectangle(
                    (x, y), w, h, linewidth=2, edgecolor="green", facecolor="none"
                )
                ax.add_patch(rect)

            # Draw predicted boxes in red
            for box in data["pred_boxes"]:
                x1, y1, x2, y2 = box
                w, h = x2 - x1, y2 - y1
                rect = Rectangle(
                    (x1, y1),
                    w,
                    h,
                    linewidth=2,
                    edgecolor="red",
                    facecolor="none",
                    linestyle="--",
                )
                ax.add_patch(rect)

            ax.set_title(f"Image {idx + 1}", fontsize=12, fontweight="bold")
            ax.axis("off")

        # Hide unused subplots
        for i in range(len(viz_images), rows * cols):
            axes[i].axis("off")

        # Add legend
        legend_elements = [
            Line2D([0], [0], color="green", linewidth=2, label="Ground Truth"),
            Line2D(
                [0], [0], color="red", linewidth=2, linestyle="--", label="Prediction"
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

    mean_ciou = float(np.mean(all_ciou_scores)) if all_ciou_scores else 0.0
    recall = correct_detections / total_predictions if total_predictions > 0 else 0.0
    avg_sample_inference_ms = float((np.mean(inference_times) * 1000) if inference_times else 0)

    return {
        "mean_ciou": mean_ciou,
        "correct_detections": correct_detections,
        "total_predictions": total_predictions,
        "total_gts": total_gts,
        "recall": recall,
        "avg_sample_inference_ms": avg_sample_inference_ms,
    }


def evaluate_model(model_path: str, config, task):
    # Get model extension
    _, ext = os.path.splitext(model_path)
    model_extension = ext[1:] if ext else "keras"  # Remove leading dot, default to keras
    is_tflite = model_extension == "tflite"
    
    if is_tflite:
        # Load TFLite model
        inference = DiceDetectionInference(
            model_path=model_path,
            image_resolution=task.image_resolution,
            colored=config.colored
        )
        logger.info(f"Loaded TFLite model from {model_path}")
    else:
        # Load Keras model
        model = tf.keras.models.load_model(model_path)
        logger.info(f"Loaded Keras model from {model_path}")

    # Get validation dataset
    logger.info("Loading validation dataset...")
    val_dataset_obj, val_dataset = get_val_dataset(config, task)

    # No separate timing loop — timings measured inside evaluate_with_ciou
    avg_sample_inference_ms = 0.0

    # Get model name from path
    model_name_base = os.path.splitext(os.path.basename(model_path))[0]
    model_name = f"{model_name_base}-{model_extension}"
    output_dir = os.path.dirname(model_path)

    # Evaluate with CIoU metric
    logger.info("Evaluating with CIoU metric...")
    ciou_metrics = evaluate_with_ciou(
        inference=inference if is_tflite else None,
        model=model if not is_tflite else None,
        val_dataset_obj=val_dataset_obj,
        val_dataset=val_dataset,
        image_resolution=task.image_resolution,
        iou_threshold=0.5,
        output_dir=output_dir,
        model_name=model_name,
        is_tflite=is_tflite,
    )

    # Create metrics dict (use avg inference time from evaluator)
    avg_sample_inference_ms = float(ciou_metrics.get("avg_sample_inference_ms", 0.0))
    # Create metrics dict (use avg inference time from evaluator)
    avg_sample_inference_ms = float(ciou_metrics.get("avg_sample_inference_ms", 0.0))

    metrics = {
        "model": model_name_base,
        "mean_ciou": float(ciou_metrics["mean_ciou"]),
        "recall": float(ciou_metrics["recall"]),
        "correct_detections": int(ciou_metrics["correct_detections"]),
        "total_predictions": int(ciou_metrics["total_predictions"]),
        "total_gts": int(ciou_metrics["total_gts"]),
        "avg_sample_inference_ms": avg_sample_inference_ms,
        "model_type": model_extension,
    }

    # Write metrics to YAML
    yml_path = os.path.join(output_dir, "eval.yml")
    with open(yml_path, 'w') as f:
        yaml.dump(metrics, f, default_flow_style=False)
    logger.info(f"Evaluation metrics saved to {yml_path}")

    logger.info("Validation completed")
