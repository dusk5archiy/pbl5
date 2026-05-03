from src.backend.logging import logger

from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt

def plot_evaluation_results(output_pathbase: str, viz_images: list, file_extension: str="png"):
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
    viz_path = f"{output_pathbase}.{file_extension}"
    plt.tight_layout()
    plt.savefig(viz_path, dpi=300, bbox_inches="tight")
    plt.close()
    logger.info(f"Predictions visualization saved to {viz_path}")

