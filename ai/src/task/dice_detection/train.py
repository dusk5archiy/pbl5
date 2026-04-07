import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
import time

from tqdm.keras import TqdmCallback
from sklearn.model_selection import train_test_split

from src.dataset import (
    get_image_detection_datas,
    S7DatasetDiceDetection,
    make_tf_dataset,
)
from src.model.utils.load_model import load_model
from src.model.utils.determ import enable_determ
from src.model.shared.args import DiceDetectionTaskArgs
from src.config.config import ParsedConfig
from src.external.yolo_v8.bounding_box.iou import compute_ciou
from src.task.dice_detection.utils import decode_dfl


def evaluate_with_ciou(
    model,
    val_dataset,
    image_resolution: tuple[int, int],
    output_dir: str,
    timestamp: str,
    model_name: str,
    iou_threshold: float = 0.5,
):
    from matplotlib.patches import Rectangle
    from matplotlib.lines import Line2D

    all_ciou_scores = []
    total_predictions = total_gts = correct_detections = 0

    # For visualization: store first 8 images
    viz_images = []
    viz_data = {"img_count": 0}

    for images, targets in val_dataset:
        predictions = model(images, training=False)
        batch_size = tf.shape(images)[0].numpy()

        for b in range(batch_size):
            # Decode predictions
            dfl_batch = predictions["boxes"][b]
            conf_batch = predictions["classes"][b]
            pred_boxes_xyxy = decode_dfl(dfl_batch, image_resolution).numpy()
            pred_confs = (
                conf_batch.numpy()
                if hasattr(conf_batch, "numpy")
                else np.array(conf_batch)
            )
            pred_confs = pred_confs.squeeze()
            pred_boxes_filtered = pred_boxes_xyxy[pred_confs > 0.5]

            # Filter GT boxes
            gt_boxes_np = (
                targets["boxes"][b].numpy()
                if hasattr(targets["boxes"][b], "numpy")
                else np.array(targets["boxes"][b])
            )
            gt_classes_np = (
                targets["classes"][b].numpy()
                if hasattr(targets["classes"][b], "numpy")
                else np.array(targets["classes"][b])
            )
            gt_boxes_np = (
                gt_boxes_np.reshape(-1, 4) if gt_boxes_np.ndim == 1 else gt_boxes_np
            )
            gt_classes_np = (
                gt_classes_np.reshape(-1) if gt_classes_np.ndim == 0 else gt_classes_np
            )
            gt_boxes_filtered = (
                gt_boxes_np[gt_classes_np >= 0.0]
                if len(gt_boxes_np) > 0
                and gt_boxes_np.shape[0] == gt_classes_np.shape[0]
                else np.array([], dtype=np.float32).reshape(0, 4)
            )

            total_predictions += len(pred_boxes_filtered)
            total_gts += len(gt_boxes_filtered)

            # Store first 8 images for visualization
            if output_dir and timestamp and model_name and viz_data["img_count"] < 8:
                viz_images.append(
                    {
                        "img": (images[b].numpy() * 255).astype(np.uint8),
                        "gt_boxes": gt_boxes_filtered,
                        "pred_boxes": pred_boxes_filtered,
                    }
                )
                viz_data["img_count"] += 1

            if len(pred_boxes_filtered) == 0 or len(gt_boxes_filtered) == 0:
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

    # Generate visualization of first 8 images
    if output_dir and timestamp and model_name and len(viz_images) > 0:
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
        viz_path = os.path.join(output_dir, f"{model_name}-{timestamp}-predictions.png")
        plt.tight_layout()
        plt.savefig(viz_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Predictions visualization saved to {viz_path}")

    mean_ciou = float(np.mean(all_ciou_scores)) if all_ciou_scores else 0.0
    recall = correct_detections / total_predictions if total_predictions > 0 else 0.0

    return {
        "mean_ciou": mean_ciou,
        "correct_detections": correct_detections,
        "total_predictions": total_predictions,
        "total_gts": total_gts,
        "recall": recall,
    }


def train_savedmodel(
    model_name: str,
    config: ParsedConfig,
    task: ParsedConfig.Tasks.DiceDetection,
    train_workers: int = 4,
    val_workers: int = 4,
):
    if not config.use_random:
        enable_determ()

    print("Loading dataset...")
    all_image_datas = get_image_detection_datas(
        dataset_path=config.dataset_path, num_workers=config.num_workers
    )
    print(f"Total image datas: {len(all_image_datas)}")

    # Split into 70% train and 30% validation
    train_datas, val_datas = train_test_split(
        all_image_datas, test_size=0.3, random_state=42
    )

    print(f"Train datas: {len(train_datas)}")
    print(f"Val datas: {len(val_datas)}")

    # Create datasets with split datas
    train_dataset_obj = S7DatasetDiceDetection(
        image_resolution=task.image_resolution,
        image_datas=train_datas,
        colored=config.colored,
        use_random=config.use_random,
        cache_path="output/dice_detection_train",
        dataset_repeat=task.train_dataset_repeat,
        num_workers=train_workers,
    )

    val_dataset_obj = S7DatasetDiceDetection(
        image_resolution=task.image_resolution,
        image_datas=val_datas,
        colored=config.colored,
        use_random=config.use_random,
        cache_path="output/dice_detection_val",
        dataset_repeat=task.val_dataset_repeat,
        num_workers=val_workers,
    )

    train_dataset = make_tf_dataset(
        train_dataset_obj,
        batch_size=task.batch_size,
        image_resolution=task.image_resolution,
        colored=config.colored,
    )

    val_dataset = make_tf_dataset(
        val_dataset_obj,
        batch_size=task.batch_size,
        image_resolution=task.image_resolution,
        colored=config.colored,
    )

    # Load model
    model = load_model(
        task="dice_detection",
        model_name=model_name,
        task_args=DiceDetectionTaskArgs(colored=config.colored),
    )

    # Compile model
    model.compile(
        optimizer="adam",
        box_loss="ciou",
        classification_loss="binary_crossentropy",
    )

    print("Model compiled successfully")
    model.summary()

    # Get model parameter count for metadata
    total_params = model.count_params()

    # Callbacks
    timestamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    train_output_path = f"output/{model_name}-{timestamp}.keras"
    callbacks = [
        TqdmCallback(verbose=1),
        tf.keras.callbacks.ModelCheckpoint(
            filepath=train_output_path,
            save_best_only=True,
            monitor="val_loss",
            mode="min",
        ),
    ]

    if config.use_random:
        callbacks.append(
            tf.keras.callbacks.EarlyStopping(
                monitor="val_loss", patience=10, restore_best_weights=True
            ),
        )

    # Train the model
    print("Starting training...")
    if not config.use_random:
        enable_determ()

    history = model.fit(
        train_dataset,
        validation_data=val_dataset,
        epochs=task.epochs,
        callbacks=callbacks,
        verbose=0,
    )

    # Measure average inference time and test model on validation set
    print("Evaluating model on validation set...")
    inference_times = []

    for images, targets in val_dataset:
        start_time = time.time()
        _ = model.predict(images, verbose=0)
        inference_times.append(time.time() - start_time)

    avg_batch_inference_ms = (np.mean(inference_times) * 1000) if inference_times else 0
    avg_sample_inference_ms = (
        avg_batch_inference_ms / task.batch_size if task.batch_size > 0 else 0
    )

    # Get output directory from path
    output_dir = os.path.dirname(train_output_path)
    os.makedirs(output_dir, exist_ok=True)

    # Evaluate with CIoU metric on validation data
    print("Evaluating with CIoU metric...")
    ciou_metrics = evaluate_with_ciou(
        model=model,
        val_dataset=val_dataset,
        image_resolution=task.image_resolution,
        iou_threshold=0.5,
        output_dir=output_dir,
        timestamp=timestamp,
        model_name=model_name,
    )

    # Plot training and validation loss
    print("Generating training history plot...")
    epochs_range = range(1, len(history.history["loss"]) + 1)

    # Define plotting functions
    def add_box_loss_plot(ax):
        ax.plot(
            epochs_range,
            history.history.get("box_loss", []),
            "b-",
            label="Training Box Loss",
        )
        ax.plot(
            epochs_range,
            history.history.get("val_box_loss", []),
            "r-",
            label="Validation Box Loss",
        )
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Loss (log scale)")
        ax.set_title("Training and Validation Box Loss")
        ax.set_yscale("log")
        ax.legend()
        ax.grid(True, which="both", alpha=0.3)

    def add_classification_loss_plot(ax):
        ax.plot(
            epochs_range,
            history.history.get("class_loss", []),
            "b-",
            label="Training Classification Loss",
        )
        ax.plot(
            epochs_range,
            history.history.get("val_class_loss", []),
            "r-",
            label="Validation Classification Loss",
        )
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Loss (log scale)")
        ax.set_title("Training and Validation Classification Loss")
        ax.set_yscale("log")
        ax.legend()
        ax.grid(True, which="both", alpha=0.3)

    def add_metadata(ax):
        metadata_text = (
            f"Model: {model_name}\n\nMetadata:\n"
            f"Parameters: {total_params:,}\n"
            f"Batch Size: {task.batch_size}\n"
            f"Epochs: {task.epochs}\n"
            f"Image Res: {task.image_resolution}\n"
            f"Inference: {avg_sample_inference_ms:.2f}ms/sample\n"
            f"\nCIoU Metrics:\n"
            f"Mean CIoU: {ciou_metrics['mean_ciou']:.4f}\n"
            f"Recall@0.5: {ciou_metrics['recall']:.4f}"
        )

        ax.axis("off")
        ax.text(
            0.1,
            0.95,
            metadata_text,
            transform=ax.transAxes,
            verticalalignment="top",
            horizontalalignment="left",
            bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.8, pad=1),
            fontsize=10,
            family="monospace",
        )

    # Create figure with GridSpec for layout: 2 plots on left, metadata on right
    fig = plt.figure(figsize=(16, 5))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 0.8], hspace=0.3)

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[0, 2])

    # Call plotting functions with respective axes
    add_metadata(ax1)
    add_box_loss_plot(ax2)
    add_classification_loss_plot(ax3)

    plot_path = os.path.join(output_dir, f"{model_name}-{timestamp}.png")
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Training history plot saved to {plot_path}")
