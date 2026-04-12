from typing import Any
import matplotlib.pyplot as plt
import os
from pydantic import validate_call
from src.backend.logging import logger

@validate_call
def plot_training_history(
    path_base: str,
    history: Any,
    file_extension: str="png"
):
    # Plot training and validation loss
    logger.info("Generating training history plot...")
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

    # def add_metadata(ax):
    fig = plt.figure(figsize=(16, 5))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1], hspace=0.3)

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    # Call plotting functions with respective axes
    # add_metadata(ax1)
    add_box_loss_plot(ax1)
    add_classification_loss_plot(ax2)

    filename = f"{path_base}.{file_extension}"
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()
    logger.success(f"Training history plot saved to {filename}")


@validate_call
def plot_evaluation_results(path_base: str, viz_images: list, file_extension: str="png"):
    from matplotlib.patches import Rectangle
    from matplotlib.lines import Line2D

    if len(viz_images) == 0:
        return

    rows, cols = 4, 2
    fig, axes = plt.subplots(rows, cols, figsize=(12, 16), dpi=80)
    axes = axes.flatten()

    for idx, data in enumerate(viz_images):
        ax = axes[idx]
        ax.imshow(data["img"].squeeze(), cmap="gray", vmin=0, vmax=255)

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
    filename = f"{path_base}.{file_extension}"
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()
    logger.info(f"Predictions visualization saved to {filename}")

