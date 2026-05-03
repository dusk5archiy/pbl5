from .plot import plot_training_history
from .dataset import load_dataset
from .report import report_training_results

from src.backend.logging import logger
from src.config import ParsedConfig
from src.model.shared.args import DiceDetectionTaskArgs
from src.composables.model import load_model
from src.utils.determ import enable_determ

from tqdm.keras import TqdmCallback
import tensorflow as tf

from datetime import datetime
import os


def train_savedmodel(
    model_name: str,
    config: ParsedConfig,
    task: ParsedConfig.Tasks.DiceDetection,
    batch_size: int,
    epochs: int,
    train_workers: int = 4,
    val_workers: int = 4,
):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_dir = f"output/{task.name}/{model_name}/{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    model_filepath = f"{output_dir}/model.keras"

    if not config.use_random:
        enable_determ()

    train_dataset, val_dataset = load_dataset(
        config=config,
        task=task,
        batch_size=batch_size,
        train_workers=train_workers,
        val_workers=val_workers
    )

    model = load_model(
        task="dice_detection",
        model_name=model_name,
        task_args=DiceDetectionTaskArgs(
            colored=config.colored,
            image_resolution=task.image_resolution,
        ),
    )

    # Compile model
    model.compile(
        optimizer="adam",
        box_loss="ciou",
        classification_loss="binary_crossentropy",
    )

    logger.success("Model compiled successfully")
    model.summary()

    # Get model parameter count for metadata

    # Callbacks
    callbacks = [
        TqdmCallback(verbose=1),
        tf.keras.callbacks.ModelCheckpoint(
            filepath=model_filepath,
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
    logger.info("Starting training...")
    if not config.use_random:
        enable_determ()

    history = model.fit(
        train_dataset,
        validation_data=val_dataset,
        epochs=epochs,
        callbacks=callbacks,
        verbose=0,
    )
    
    plot_training_history(
        path_base=os.path.join(output_dir, "train"),
        history=history
    ) 

    report_training_results(
        output_dir=output_dir,
        model_name=model_name,
        model=model,
        batch_size=batch_size,
        n_epochs=epochs,
        image_resolution=task.image_resolution
    )


    logger.success(f"Training completed. Model saved to {model_filepath}")
