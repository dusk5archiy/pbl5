import tensorflow as tf
import os
import numpy as np
from training.dice_score.dataset import (
    S7DatasetDiceClassification,
    S7DatasetDiceClassificationConfig,
)

from training.dice_score.data import get_dice_crops

from tqdm.keras import TqdmCallback
from training.dice_score.model import get_dice_score_model

def train_savedmodel(dataset_path: str, output_savedmodel_dir: str, num_workers: int=4):
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
    train_dataset_obj = S7DatasetDiceClassification(
        config=S7DatasetDiceClassificationConfig(
            image_resolution=(32, 32)
        ),
        dice_crops=train_crops,
    )

    val_dataset_obj = S7DatasetDiceClassification(
        config=S7DatasetDiceClassificationConfig(
            image_resolution=(32, 32),
        ),
        dice_crops=val_crops,
    )

    # Create train and val generators
    def train_generator():
        for img, lbl in train_dataset_obj:
            yield img.astype(np.float32) / 255.0, lbl

    def val_generator():
        for img, lbl in val_dataset_obj:
            yield img.astype(np.float32) / 255.0, lbl

    train_dataset = tf.data.Dataset.from_generator(
        train_generator,
        output_signature=(tf.TensorSpec(shape=(32, 32, 3), dtype=tf.float32),
                          tf.TensorSpec(shape=(), dtype=tf.int32))
    ).batch(32)

    val_dataset = tf.data.Dataset.from_generator(
        val_generator,
        output_signature=(tf.TensorSpec(shape=(32, 32, 3), dtype=tf.float32),
                          tf.TensorSpec(shape=(), dtype=tf.int32))
    ).batch(32)

    # Create MobileNetV2 model from scratch
    # print("Creating MobileNetV2 model...")
    # base_model = MobileNetV2(weights=None, include_top=False, input_shape=(32, 32, 3))

    # TensorFlow version of DiceScoreModel
    model = get_dice_score_model()
    # Compile model
    model.compile(
        optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
    )

    print("Model compiled successfully")
    model.summary()

    # Create output directory
    os.makedirs(output_savedmodel_dir, exist_ok=True)

    # Callbacks
    callbacks = [
        TqdmCallback(verbose=1),
        tf.keras.callbacks.ModelCheckpoint(
            filepath=output_savedmodel_dir,
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
        epochs=50,
        callbacks=callbacks,
        verbose=0,  # Disable default progress bar since we use TqdmCallback
    )