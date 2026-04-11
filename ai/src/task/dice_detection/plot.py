from typing import Any
import matplotlib.pyplot as plt
from pydantic import validate_call
from src.backend.logging import logger

@validate_call
def plot_training_history(
    output_dir: str,
    history: Any,
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

    filename = f"{output_dir}/train.png"
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()
    logger.success(f"Training history plot saved to {filename}")

