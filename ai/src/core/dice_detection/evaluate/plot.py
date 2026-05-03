from src.backend.logging import logger

import matplotlib.pyplot as plt

def plot_evaluation_results(
    output_pathbase: str, viz_images: list, file_extension: str = "png"
):
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
    filename = f"{output_pathbase}.{file_extension}"
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()
    logger.info(f"Predictions visualization saved to {filename}")

