from src.backend.logging import logger

import matplotlib.pyplot as plt

from typing import Any

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
