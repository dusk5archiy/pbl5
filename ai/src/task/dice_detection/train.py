import tensorflow as tf
from tqdm.keras import TqdmCallback
from sklearn.model_selection import train_test_split

from src.dataset import (
    S7DatasetDiceDetection,
    get_image_detection_datas,
)
from .model import load_model
from src.dataset import get_image_detection_datas, make_tf_dataset


def train_savedmodel(
        dataset_path: str,
        image_resolution: tuple[int, int],  # (width, height)
        path: str,
        num_workers: int=4,
        batch_size = 8,
        epochs = 50,
        bounding_box_format = "xywh",
        learning_rate=1e-3,
        colored: bool=True,
        # train_policy="mixed_float16"
    ):
    # policy = tf.keras.mixed_precision.Policy(train_policy)
    # tf.keras.mixed_precision.set_global_policy(policy)

    IMG_W, IMG_H = image_resolution
    print("Loading dataset...")
    all_image_datas = get_image_detection_datas(
        dataset_path=dataset_path, num_workers=num_workers
    )
    train_datas, val_datas = train_test_split(all_image_datas, test_size=0.3)

    train_iterable = S7DatasetDiceDetection(
        image_resolution=image_resolution,
        image_datas=train_datas,
        num_workers=num_workers,
        colored=colored
    )

    val_iterable = S7DatasetDiceDetection(
        image_resolution=image_resolution,
        image_datas=val_datas,
        num_workers=num_workers,
        colored=colored
    )

    train_dataset = make_tf_dataset(
        train_iterable,
        batch_size=batch_size,
        image_resolution=image_resolution,
        colored=colored
    )
    val_dataset = make_tf_dataset(
        val_iterable,
        batch_size=batch_size, 
        image_resolution=image_resolution,
        colored=colored,
    )

    print("Building model...")
    model = load_model(
        bounding_box_format=bounding_box_format,
        colored=colored
    )
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        box_loss="ciou",
        classification_loss="binary_crossentropy",
    )

    print("Model compiled successfully")

    callbacks = [
        TqdmCallback(verbose=1),
        tf.keras.callbacks.ModelCheckpoint(
            filepath=path,
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
        epochs=epochs,
        callbacks=callbacks,
        verbose='0'
    )
