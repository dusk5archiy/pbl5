from .plot import plot_training_history
from .report import report_training_results
from .dataset import load_dataset

from src.backend.logging import logger
from src.config import ParsedConfig
from src.model.shared.args import DiceScoreTaskArgs
from src.composables.model import load_model
from src.utils.determ import enable_determ

from pydantic import validate_call
from tqdm.keras import TqdmCallback
import tensorflow as tf

from datetime import datetime
import os

@validate_call
def train_savedmodel(
    model_name: str,
    config: ParsedConfig,
    batch_size: int,
    epochs: int,
    task: ParsedConfig.Tasks.DiceScore,
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
        batch_size=batch_size,
        task=task,
        train_workers=train_workers,
        val_workers=val_workers,
    )

    # TensorFlow version of DiceScoreModel
    model = load_model(
        task="dice_score",
        model_name=model_name,
        task_args=DiceScoreTaskArgs(
            image_resolution=task.image_resolution, colored=config.colored
        ),
    )
    # Compile model
    model.compile(
        optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
    )

    logger.success("Model compiled successfully")
    model.summary()

    # Callbacks
    callbacks = [
        TqdmCallback(verbose=1),
        tf.keras.callbacks.ModelCheckpoint(
            filepath=model_filepath,
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

    plot_training_history(output_dir=output_dir, history=history)
    report_training_results(
        output_dir=output_dir,
        model=model,
        model_name=model_name,
        batch_size=batch_size,
        n_epochs=epochs,
        image_resolution=task.image_resolution,
    )

    logger.success(f"Training completed. Model saved to {model_filepath}")
