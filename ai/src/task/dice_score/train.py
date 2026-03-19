import tensorflow as tf
import numpy as np
from src.dataset import (
    S7DatasetDiceScore,
    get_dice_crops
)

from tqdm.keras import TqdmCallback
from .model import load_model

def train_savedmodel(
        dataset_path: str,
        path: str,
        image_resolution: tuple[int, int]=(32, 32),
        batch_size: int=32,
        epochs: int=50,
        num_workers: int=4,
        colored: bool=True,
    ):
    # Load dataset
    print("Loading dataset...")

    # Get all dice crops
    all_dice_crops = get_dice_crops(
        dataset_path=dataset_path,
        num_workers=num_workers,
    )
    print(f"Total dice crops: {len(all_dice_crops)}")

    # Split into 70% train and 30% validation
    split_index = int(len(all_dice_crops) * 0.7)
    train_crops = all_dice_crops[:split_index]
    val_crops = all_dice_crops[split_index:]

    print(f"Train crops: {len(train_crops)}")
    print(f"Val crops: {len(val_crops)}")

    # Create datasets with split crops
    train_dataset_obj = S7DatasetDiceScore(
        image_resolution=image_resolution,
        dice_crops=train_crops,
        colored=colored
    )

    val_dataset_obj = S7DatasetDiceScore(
        image_resolution=image_resolution,
        dice_crops=val_crops,
        colored=colored
    )

    # Create train and val generators
    def train_generator():
        for img, lbl in train_dataset_obj:
            yield img.astype(np.float32) / 255.0, lbl

    def val_generator():
        for img, lbl in val_dataset_obj:
            yield img.astype(np.float32) / 255.0, lbl
            
    num_channels = 3 if colored else 1
    shape = (*image_resolution, num_channels)

    train_dataset = tf.data.Dataset.from_generator(
        train_generator,
        output_signature=(tf.TensorSpec(shape=shape, dtype=tf.float32),
                          tf.TensorSpec(shape=(), dtype=tf.int32))
    ).batch(batch_size=batch_size)

    val_dataset = tf.data.Dataset.from_generator(
        val_generator,
        output_signature=(tf.TensorSpec(shape=shape, dtype=tf.float32),
                          tf.TensorSpec(shape=(), dtype=tf.int32))
    ).batch(batch_size=batch_size)

    # TensorFlow version of DiceScoreModel
    model = load_model(image_resolution=image_resolution, channels=num_channels)
    # Compile model
    model.compile(
        optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
    )

    print("Model compiled successfully")
    model.summary()

    # Callbacks
    callbacks = [
        TqdmCallback(verbose=1),
        tf.keras.callbacks.ModelCheckpoint(
            filepath=path,
            save_best_only=True,
            monitor="val_accuracy",
            mode="max",
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=10, restore_best_weights=True
        ),
    ]

    # Train the model
    print("Starting training...")
    model.fit(
        train_dataset,
        validation_data=val_dataset,
        epochs=epochs,
        callbacks=callbacks,
        verbose=0,  # Disable default progress bar since we use TqdmCallback
    )