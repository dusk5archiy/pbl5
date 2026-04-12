from pydantic import validate_call
from typing import Any
import matplotlib.pyplot as plt
from src.backend.logging import logger
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os

def plot_training_history(
    output_dir: str,
    history: Any
):
    # Get output directory from path
    # Plot training and validation loss and accuracy
    logger.info("Generating training history plot...")
    epochs_range = range(1, len(history.history["loss"]) + 1)

    # Define plotting functions
    def add_loss_plot(ax):
        ax.plot(
            epochs_range,
            history.history.get("loss", []),
            "b-",
            label="Training Loss",
        )
        ax.plot(
            epochs_range,
            history.history.get("val_loss", []),
            "r-",
            label="Validation Loss",
        )
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Loss (log scale)")
        ax.set_title("Training and Validation Loss")
        ax.set_yscale("log")
        ax.legend()
        ax.grid(True, which="both", alpha=0.3)

    def add_accuracy_plot(ax):
        ax.plot(
            epochs_range,
            history.history.get("accuracy", []),
            "b-",
            label="Training Accuracy",
        )
        ax.plot(
            epochs_range,
            history.history.get("val_accuracy", []),
            "r-",
            label="Validation Accuracy",
        )
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Accuracy")
        ax.set_title("Training and Validation Accuracy")
        ax.legend()
        ax.grid(True, which="both", alpha=0.3)

    fig = plt.figure(figsize=(16, 5))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1], hspace=0.3)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    # Call plotting functions with respective axes
    add_loss_plot(ax1)
    add_accuracy_plot(ax2)

    filename = f"{output_dir}/train.png"
    plt.tight_layout()
    plt.savefig(f"{output_dir}/train.png", dpi=300, bbox_inches="tight")
    plt.close()
    logger.success(f"Training history plot saved to {filename}")

def plot_evaluation_results(path_base: str, viz_images: list, file_extension: str="png"):
    # Generate visualization of first 8 images
    if len(viz_images) == 0:
        return
    rows, cols = 4, 2
    fig, axes = plt.subplots(rows, cols, figsize=(12, 16), dpi=80)
    axes = axes.flatten()

    for idx, data in enumerate(viz_images):
        ax = axes[idx]
        ax.imshow(
            data["img"].squeeze(),
            cmap="gray" if data["img"].shape[-1] == 1 else None,
            vmin=0, vmax=255,
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
    viz_path = f"{path_base}.{file_extension}"
    plt.tight_layout()
    plt.savefig(viz_path, dpi=300, bbox_inches="tight")
    plt.close()
    logger.info(f"Predictions visualization saved to {viz_path}")
