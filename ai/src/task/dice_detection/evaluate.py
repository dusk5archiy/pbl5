import tensorflow as tf
import numpy as np
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
from src.task.dice_detection.inference import DotKerasInference, DotTfliteInference
from src.model.shared.args import DiceDetectionTaskArgs
from src.task.dice_detection.plot import plot_evaluation_results
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


def evaluate_model(model_path: str, config, task):
    # Get model extension
    _, ext = os.path.splitext(model_path)
    model_extension = ext[1:] if ext else "keras"  # Remove leading dot, default to keras

    # Create args
    args = DiceDetectionTaskArgs(
        colored=config.colored,
        image_resolution=task.image_resolution,
    )

    if model_extension == "tflite":
        inference = DotTfliteInference(model_path, args)
        logger.info(f"Loaded TFLite model from {model_path}")
    else:
        inference = DotKerasInference(model_path, args)
        logger.info(f"Loaded Keras model from {model_path}")

    # Get validation dataset
    logger.info("Loading validation dataset...")
    val_dataset_obj, val_dataset = get_val_dataset(config, task)

    # Get model name from path
    model_name_base = os.path.splitext(os.path.basename(model_path))[0]
    output_dir = os.path.dirname(model_path)

    # Evaluate with CIoU metric
    logger.info("Evaluating with CIoU metric...")
    all_ciou_scores = []
    total_predictions = total_gts = correct_detections = 0
    inference_times = []

    # For visualization: store first 8 images
    viz_images = []
    viz_data = {"img_count": 0}

    processed_samples = 0
    total_inference_time = 0.0

    # Iterate dataset with progress bar
    with tqdm(total=len(val_dataset_obj), desc="Evaluating", unit="sample") as pbar:
        # Iterate over batches
        for images, targets in val_dataset:
            # Iterate samples in the batch without using explicit numeric indices
            for img_tensor, target_boxes, target_classes in zip(
                images, targets["boxes"], targets["classes"]
            ):
                img = img_tensor.numpy()
                start_time = time.perf_counter()
                pred_boxes = inference(img)
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                inference_times.append(elapsed)
                processed_samples += 1
                total_inference_time += elapsed
                pbar.update(1)
                pbar.set_postfix(
                    last_sample_ms=f"{elapsed * 1000:.2f}",
                )

                # Capture for visualization after inference
                if viz_data["img_count"] < 8:
                    img_display = (img_tensor.numpy() * 255).astype(np.uint8)
                    gt_boxes = target_boxes.numpy() if hasattr(target_boxes, "numpy") else np.array(target_boxes)
                    pred_boxes_viz = pred_boxes
                    viz_images.append(
                        {
                            "img": img_display,
                            "gt_boxes": gt_boxes,
                            "pred_boxes": pred_boxes_viz,
                        }
                    )
                    viz_data["img_count"] += 1
            gt_boxes = tf.reshape(target_boxes, (-1, 4)) if tf.rank(target_boxes) == 1 else target_boxes
            gt_classes = tf.reshape(target_classes, (-1,)) if tf.rank(target_classes) == 0 else target_classes

            gt_boxes = gt_boxes[gt_classes >= 0]

            # Use tensor shapes
            total_predictions += int(tf.shape(pred_boxes)[0])
            total_gts += int(tf.shape(gt_boxes)[0])

            if len(pred_boxes) == 0 or len(gt_boxes) == 0:
                # No GT or no predictions — progress already updated during inference
                continue

            # Convert GT to xyxy
            gt_boxes_xyxy = tf.stack([
                gt_boxes[:, 0],
                gt_boxes[:, 1],
                gt_boxes[:, 0] + gt_boxes[:, 2],
                gt_boxes[:, 1] + gt_boxes[:, 3],
            ], axis=1)

            ciou_matrix = compute_ciou(
                tf.expand_dims(
                    tf.constant(pred_boxes, dtype=tf.float32), axis=1
                ),
                tf.expand_dims(tf.constant(gt_boxes_xyxy, dtype=tf.float32), axis=0),
                bounding_box_format="xyxy",
            ).numpy()

            # Track matched GTs
            matched = set()
            for i in range(len(pred_boxes)):
                best_ciou = float(np.max(ciou_matrix[i, :]))
                all_ciou_scores.append(best_ciou)
                if best_ciou <= args.iou_threshold:
                    continue

                # Find the GT index with max CIoU
                gt_idx = int(np.argmax(ciou_matrix[i, :]))
                if gt_idx not in matched:
                    matched.add(gt_idx)
                    correct_detections += 1

    plot_evaluation_results(path_base=f"{output_dir}/eval-{model_extension}", viz_images=viz_images)

    mean_ciou = float(np.mean(all_ciou_scores)) if all_ciou_scores else 0.0
    precision = correct_detections / total_predictions if total_predictions > 0 else 0.0
    recall = correct_detections / total_gts if total_gts > 0 else 0.0
    # Calculate average inference time using only the last 10 records
    last_n_inference_times = inference_times[-10:] if len(inference_times) >= 10 else inference_times
    avg_sample_inference_ms = float((np.mean(last_n_inference_times) * 1000) if last_n_inference_times else 0)

    metrics = {
        "model": model_name_base,
        "mean_ciou": mean_ciou,
        "precision": precision,
        "recall": recall,
        "correct_detections": correct_detections,
        "total_predictions": total_predictions,
        "total_gts": total_gts,
        "avg_sample_inference_ms": avg_sample_inference_ms,
        "model_type": model_extension,
    }

    # Write metrics to YAML
    yml_path = f"{output_dir}/eval-{model_extension}.yml"    
    with open(yml_path, 'w') as f:
        yaml.dump(metrics, f, default_flow_style=False)
    logger.info(f"Evaluation metrics saved to {yml_path}")

    logger.info("Evaluation completed")
