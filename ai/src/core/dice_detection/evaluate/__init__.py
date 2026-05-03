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

import time


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
    logger.info("Loading validation dataset...")
    val_dataset_obj, val_dataset = load_dataset(config, task)

    # Get model name from path

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
                pred_boxes = inference.model(img)
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

            gt_boxes = get_gt_boxes(
                target_boxes=target_boxes, target_classes=target_classes
            )

            total_predictions += int(tf.shape(pred_boxes)[0])
            total_gts += int(tf.shape(gt_boxes)[0])

            if len(pred_boxes) == 0 or len(gt_boxes) == 0:
                continue

            best_ciou_scores, n_corrects = count_correct_detections(
                pred_boxes=pred_boxes,
                gt_boxes=gt_boxes,
                iou_threshold=args.iou_threshold,
            )

            all_ciou_scores.extend(best_ciou_scores)
            correct_detections += n_corrects

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
