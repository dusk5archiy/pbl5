import tensorflow as tf
import numpy as np
from datetime import datetime
import os
from src.backend.logging import logger
from .plot import plot_training_history
from .report import report_training_results

from tqdm.keras import TqdmCallback
from sklearn.model_selection import train_test_split

from src.dataset import (
    get_image_detection_datas,
    S7DatasetDiceDetection,
)
from src.dataset.dice_detection.tf import make_tf_dataset
from src.model.utils.load_model import load_model
from src.model.utils.determ import enable_determ
from src.model.shared.args import DiceDetectionTaskArgs
from src.config.config import ParsedConfig

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

    all_image_datas = get_image_detection_datas(
        dataset_path=config.dataset_path, num_workers=config.num_workers
    )
    # Split into 70% train and 30% validation
    train_datas, val_datas = train_test_split(
        all_image_datas, test_size=0.3, random_state=42
    )

    # Create datasets with split datas
    train_dataset_obj = S7DatasetDiceDetection(
        image_resolution=task.image_resolution,
        image_datas=train_datas,
        colored=config.colored,
        use_random=config.use_random,
        cache_path="output/dice_detection_train",
        dataset_repeat=task.train_dataset_repeat,
        num_workers=train_workers,
    )

    val_dataset_obj = S7DatasetDiceDetection(
        image_resolution=task.image_resolution,
        image_datas=val_datas,
        colored=config.colored,
        use_random=config.use_random,
        cache_path="output/dice_detection_val",
        dataset_repeat=task.val_dataset_repeat,
        num_workers=val_workers,
    )

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

    # Load model
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