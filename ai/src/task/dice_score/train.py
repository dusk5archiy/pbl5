import tensorflow as tf
import numpy as np
from tqdm import tqdm
from src.dataset import S7DatasetDiceScore, get_dice_crops

from tqdm.keras import TqdmCallback
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
from datetime import datetime
from src.model.utils.load_model import load_model
from src.model.utils.determ import enable_determ
from src.model.shared.args import DiceScoreTaskArgs 
from src.config.config import ParsedConfig
import os


def train_savedmodel(
    model_name: str,
    config: ParsedConfig,
    task: ParsedConfig.Tasks.DiceScore,
    train_workers: int = 4,
    val_workers: int = 4,
):
    if not config.use_random:
        enable_determ()

    # Get all dice crops
    all_dice_crops = get_dice_crops(
        dataset_path=config.dataset_path,
        num_workers=config.num_workers,
    )

    # Split into 70% train and 30% validation
    train_crops, val_crops = train_test_split(all_dice_crops, test_size=0.3, random_state=42)

    # Create datasets with split crops
    train_dataset_obj = S7DatasetDiceScore(
        image_resolution=task.image_resolution,
        dice_crops=train_crops,
        colored=config.colored,
        num_workers=train_workers,
        use_random=config.use_random,
        dataset_repeat=task.train_dataset_repeat,
        cache_path="output/dice_score_train"
    )

    val_dataset_obj = S7DatasetDiceScore(
        image_resolution=task.image_resolution,
        dice_crops=val_crops,
        colored=config.colored,
        num_workers=val_workers,
        use_random=config.use_random,
        dataset_repeat=task.val_dataset_repeat,
        cache_path="output/dice_score_val"
    )

    # Create train and val generators
    def train_generator():
        for img, lbl in train_dataset_obj:
            yield img.astype(np.float32) / 255.0, lbl

    def val_generator():
        for img, lbl in val_dataset_obj:
            yield img.astype(np.float32) / 255.0, lbl

    num_channels = 3 if config.colored else 1
    shape = (*(task.image_resolution), num_channels)

    train_dataset = tf.data.Dataset.from_generator(
        train_generator,
        output_signature=(
            tf.TensorSpec(shape=shape, dtype=tf.float32),
            tf.TensorSpec(shape=(), dtype=tf.int32),
        ),
    ).batch(batch_size=task.batch_size)

    val_dataset = tf.data.Dataset.from_generator(
        val_generator,
        output_signature=(
            tf.TensorSpec(shape=shape, dtype=tf.float32),
            tf.TensorSpec(shape=(), dtype=tf.int32),
        ),
    ).batch(batch_size=task.batch_size)

    # TensorFlow version of DiceScoreModel
    model = load_model(
        task="dice_score",
        model_name=model_name,
        task_args=DiceScoreTaskArgs(image_resolution=task.image_resolution, colored=config.colored),
    )
    # Compile model
    model.compile(
        optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
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
            monitor="val_accuracy",
            mode="max",
        ),
    ]

    if config.use_random:
        callbacks.append(
            tf.keras.callbacks.EarlyStopping(
                monitor="val_accuracy", patience=10, restore_best_weights=True
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

    # Get output directory from path
    output_dir = os.path.dirname(train_output_path)
    os.makedirs(output_dir, exist_ok=True)

    # Calculate precision, recall, and F1 score on validation set
    print("Calculating metrics on validation set...")
    all_true_labels = []
    all_predictions = []

    for batch_images, batch_labels in tqdm(val_dataset):
        preds = model.predict_on_batch(batch_images)
        pred_labels = np.argmax(preds, axis=1)
        all_true_labels.extend(np.asarray(batch_labels))
        all_predictions.extend(pred_labels)

    all_true_labels = np.array(all_true_labels)
    all_predictions = np.array(all_predictions)

    precision = precision_score(
        all_true_labels, all_predictions, average="weighted", zero_division=0
    )
    recall = recall_score(
        all_true_labels, all_predictions, average="weighted", zero_division=0
    )
    f1 = f1_score(all_true_labels, all_predictions, average="weighted", zero_division=0)

    # Plot training and validation loss and accuracy
    print("Generating training history plot...")
    epochs_range = range(1, len(history.history["loss"]) + 1)

    # Create figure with GridSpec for layout: 2 plots on left, metadata on right
    fig = plt.figure(figsize=(16, 5))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 0.8], hspace=0.3)
    
    def add_loss_plot(ax):
        ax.plot(epochs_range, history.history["loss"], "b-", label="Training Loss")
        ax.plot(epochs_range, history.history["val_loss"], "r-", label="Validation Loss")
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Loss")
        ax.set_title("Training and Validation Loss")
        ax.legend()
        ax.grid(True)

    def add_acc_plot(ax):
        # Plot accuracy
        ax.plot(epochs_range, history.history["accuracy"], "b-", label="Training Accuracy")
        ax.plot(
            epochs_range, history.history["val_accuracy"], "r-", label="Validation Accuracy"
        )
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Accuracy")
        ax.set_title("Training and Validation Accuracy")
        ax.legend()
        ax.grid(True)

        
    def add_metadata(ax):
        metadata_text = f"Model: {model_name}\n\nMetadata:\n" \
                       f"Parameters: {total_params:,}\n" \
                       f"Train Dataset Repeat: {task.train_dataset_repeat:,}\n" \
                       f"Val Dataset Repeat: {task.val_dataset_repeat:,}\n" \
                       f"Parameters: {total_params:,}\n" \
                       f"Batch Size: {task.batch_size}\n" \
                       f"Epochs: {task.epochs}\n" \
                       f"Image Res: {task.image_resolution}\n\n" \
                       f"Validation Metrics:\n" \
                       f"Precision: {precision:.4f}\n" \
                       f"Recall: {recall:.4f}\n" \
                       f"F1 Score: {f1:.4f}"
        
        ax.axis('off')
        ax.text(0.1, 0.95, metadata_text, transform=ax.transAxes,
                 verticalalignment='top', horizontalalignment='left',
                 bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8, pad=1),
                 fontsize=10, family='monospace')

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[0, 2])

    add_metadata(ax1)
    add_loss_plot(ax2)
    add_acc_plot(ax3)

    plot_path = os.path.join(output_dir, f"{model_name}-{timestamp}.png")
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Training history plot saved to {plot_path}")
