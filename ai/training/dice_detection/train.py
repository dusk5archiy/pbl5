import os

import numpy as np
import tensorflow as tf
from tqdm.keras import TqdmCallback
from sklearn.model_selection import train_test_split

from .dataset import (
    S7DatasetDiceDetection,
    S7DatasetDiceDetectionConfig,
    get_image_detection_datas,
)
from .model import get_dice_detection_model

IMAGE_RESOLUTION = (640, 480)  # (width, height)
IMG_W, IMG_H = IMAGE_RESOLUTION
NUM_CLASSES = 1  # Only dice (one class)
BATCH_SIZE = 8
EPOCHS = 50
BOUNDING_BOX_FORMAT = "xywh"

def train_savedmodel(dataset_path: str, output_savedmodel_dir: str, num_workers: int=4):

    print("Loading dataset...")
    all_image_datas = get_image_detection_datas(
        dataset_path=dataset_path, num_workers=num_workers
    )
    train_datas, val_datas = train_test_split(all_image_datas, test_size=0.3)

    det_config = S7DatasetDiceDetectionConfig(
        dataset_path=dataset_path,
        image_resolution=IMAGE_RESOLUTION,
    )

    train_dataset_obj = S7DatasetDiceDetection(
        config=det_config,
        image_datas=train_datas,
        num_workers=num_workers,
    )

    val_dataset_obj = S7DatasetDiceDetection(
        config=det_config,
        image_datas=val_datas,
        num_workers=num_workers,
    )

    def make_tf_dataset(dataset_obj):
        def generator():
            for img_array, bboxes in dataset_obj:
                img = img_array.astype(np.float32) / 255.0
                if bboxes:
                    boxes = np.array(bboxes, dtype=np.float32)
                else:
                    boxes = np.zeros((0, 4), dtype=np.float32)
                classes = np.zeros(len(boxes), dtype=np.float32)  # dummy class 1
                yield img, boxes, classes

        ds = tf.data.Dataset.from_generator(
            generator,
            output_signature=(
                tf.TensorSpec(shape=(IMG_H, IMG_W, 3), dtype=tf.float32),
                tf.TensorSpec(shape=(None, 4), dtype=tf.float32),
                tf.TensorSpec(shape=(None,), dtype=tf.float32),
            ),
        ).padded_batch(
            BATCH_SIZE,
            padded_shapes=([IMG_H, IMG_W, 3], [None, 4], [None]), # type: ignore
            padding_values=(0.0, -1.0, -1.0),
        )

        # Convert padded dense tensors to ragged tensors and pack into the
        # dict format keras_cv YOLOV8Detector expects.
        # Use a boolean mask: a box row is padding if all 4 coords equal -1.
        def to_model_input(images, boxes_padded, classes_padded):
            valid_mask = tf.reduce_any(boxes_padded != -1.0, axis=-1)  # [B, N]
            boxes_ragged = tf.ragged.boolean_mask(boxes_padded, valid_mask)
            classes_ragged = tf.ragged.boolean_mask(classes_padded, valid_mask)
            return images, {"boxes": boxes_ragged, "classes": classes_ragged}

        return ds.map(to_model_input, num_parallel_calls=tf.data.AUTOTUNE)

    train_dataset = make_tf_dataset(train_dataset_obj)
    val_dataset = make_tf_dataset(val_dataset_obj)

    print("Building model...")
    model = get_dice_detection_model(
        num_classes=NUM_CLASSES,
        bounding_box_format=BOUNDING_BOX_FORMAT,
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        box_loss="ciou",
        classification_loss="binary_crossentropy",
    )

    print("Model compiled successfully")
    model.summary()

    os.makedirs(output_savedmodel_dir, exist_ok=True)

    callbacks = [
        TqdmCallback(verbose=1),
        tf.keras.callbacks.ModelCheckpoint(
            filepath=output_savedmodel_dir,
            save_best_only=True,
            monitor="val_loss",
            mode="min",
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=10, restore_best_weights=True
        ),
    ]

    print("Starting training...")
    model.fit(
        train_dataset,
        validation_data=val_dataset,
        epochs=EPOCHS,
        callbacks=callbacks,
        verbose='0'
    )