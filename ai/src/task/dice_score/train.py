import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from src.dataset import S7DatasetDiceScore, get_dice_crops
from src.dataset.dice_score.tf import make_tf_dataset
from tqdm.keras import TqdmCallback
from sklearn.model_selection import train_test_split
from datetime import datetime
from src.model.utils.load_model import load_model
from src.model.utils.determ import enable_determ
from src.model.shared.args import DiceScoreTaskArgs 
from src.config.config import ParsedConfig
import os
from pydantic import validate_call
from .plot import plot_training_history
from .report import report_training_results
from src.backend.logging import logger


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

    # Create train and val datasets using make_tf_dataset
    train_dataset = make_tf_dataset(
        train_dataset_obj,
        batch_size=batch_size,
        image_resolution=task.image_resolution,
        colored=config.colored,
        use_random=config.use_random
    )

    val_dataset = make_tf_dataset(
        val_dataset_obj,
        batch_size=batch_size,
        image_resolution=task.image_resolution,
        colored=config.colored,
        use_random=config.use_random
    )

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
        image_resolution=task.image_resolution
    )

    logger.success(f"Training completed. Model saved to {model_filepath}")