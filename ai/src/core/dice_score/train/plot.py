from src.backend.logging import logger

import matplotlib.pyplot as plt

from typing import Any

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