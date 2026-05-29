from .dataset import load_dataset
from .functions import count_correct_detections, get_gt_boxes
from .report import report
from .plot import plot_evaluation_results

from src.backend.logging import logger
from src.config import ParsedConfig
from src.utils.file import split_path
from src.core.dice_detection.inference import DiceDetectionInference
from src.model.shared.args import DiceDetectionTaskArgs

from tqdm import tqdm
import numpy as np
import tensorflow as tf
import os
import time

# Suppress internal TensorFlow rendezvous info logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"


def evaluate_model(
    model_path: str, config: ParsedConfig, task: ParsedConfig.Tasks.DiceDetection
):
    output_dir, model_basename, model_ext = split_path(
        filepath=model_path, default_ext="keras"
    )
    output_pathbase=f"{output_dir}/eval-{model_ext}"

    # Create args
    args = DiceDetectionTaskArgs(
        colored=config.colored,
        image_resolution=task.image_resolution,
    )

    inference = DiceDetectionInference(
        model_path=model_path,
        image_resolution=task.image_resolution,
        colored=config.colored,
        conf_threshold=args.conf_threshold,
        iou_threshold=args.iou_threshold,
    )

    # Get validation dataset
    logger.info("Loading validation dataset for timing (Batch 1)...")
    val_dataset_obj, time_dataset = load_dataset(config, task, batch_size=1)

    # 1. Measurement of average inference time (10 samples)
    logger.info("Measuring inference time (10 samples)...")
    inference_times = []
    time_samples_count = 0
    total_samples_for_time = 10
    
    for images, _ in time_dataset:
        for img_tensor in images:
            img = img_tensor.numpy()
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

    logger.info("Evaluating accuracy on full dataset...")
    all_ciou_scores = []
    total_predictions = total_gts = correct_detections = 0

    # For visualization: store first 8 images
    viz_images = []
    viz_data = {"img_count": 0}

    # Iterate dataset with progress bar
    with tqdm(total=test_count, desc="Accuracy Eval", unit="sample") as pbar:
        # Iterate over batches
        try:
            for images, targets in val_dataset:
                # Iterate samples in the batch without using explicit numeric indices
                for img_tensor, target_boxes, target_classes in zip(
                    images, targets["boxes"], targets["classes"]
                ):
                    img = img_tensor.numpy()
                    pred_boxes = inference.model(img)
                    pbar.update(1)

                    # Capture for visualization after inference
                    if viz_data["img_count"] < 8:
                        img_display = (img_tensor.numpy() * 255).astype(np.uint8)
                        gt_boxes = (
                            target_boxes.numpy()
                            if hasattr(target_boxes, "numpy")
                            else np.array(target_boxes)
                        )
                        pred_boxes_viz = pred_boxes
                        viz_images.append(
                            {
                                "img": img_display,
                                "gt_boxes": gt_boxes,
                                "pred_boxes": pred_boxes_viz,
                            }
                        )
                        viz_data["img_count"] += 1

                    # Calculate metrics for this specific sample
                    sample_gt_boxes = get_gt_boxes(
                        target_boxes=target_boxes, target_classes=target_classes
                    )
                    
                    total_predictions += int(tf.shape(pred_boxes)[0])
                    total_gts += int(tf.shape(sample_gt_boxes)[0])

                    if len(pred_boxes) > 0 and len(sample_gt_boxes) > 0:
                        best_ciou_scores, n_corrects = count_correct_detections(
                            pred_boxes=pred_boxes,
                            gt_boxes=sample_gt_boxes,
                            iou_threshold=args.iou_threshold,
                        )
                        all_ciou_scores.extend(best_ciou_scores)
                        correct_detections += n_corrects
        except (tf.errors.OutOfRangeError, StopIteration):
            logger.info("End of dataset reached (OutOfRange).")

    plot_evaluation_results(
        output_pathbase=output_pathbase, viz_images=viz_images
    )

    report(
        all_ciou_scores=all_ciou_scores,
        correct_detections=correct_detections,
        total_predictions=total_predictions,
        total_gts=total_gts,
        inference_times=inference_times,
        model_basename=model_basename,
        output_pathbase=output_pathbase,
    )
