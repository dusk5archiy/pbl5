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
from keras import mixed_precision

from datetime import datetime
import os


def train_savedmodel(
    model_name: str,
    config: ParsedConfig,
    task: ParsedConfig.Tasks.DiceDetection,
    batch_size: int,
    lr: float,
    epochs: int,
    alias: str | None = None,
):
    output_suffix = alias if alias else datetime.now().strftime("%Y%m%d%H%M%S")
    output_dir = f"output/{task.name}/{model_name}/{output_suffix}"
    os.makedirs(output_dir, exist_ok=True)
    model_filepath = f"{output_dir}/model.keras"

    if not config.use_random:
        enable_determ()

    policy = mixed_precision.Policy("mixed_float16")
    mixed_precision.set_global_policy(policy)
    logger.info(f"Mixed precision policy set to: {policy.name}")

    strategy = tf.distribute.MirroredStrategy()
    logger.info(f"Number of devices in strategy: {strategy.num_replicas_in_sync}")
    tf.config.optimizer.set_jit(False)

    train_dataset, val_dataset = load_dataset(
        config=config,
        task=task,
        batch_size=batch_size,
    )

    with strategy.scope():
        model = load_model(
            task="dice_detection",
            model_name=model_name,
            task_args=DiceDetectionTaskArgs(
                colored=config.colored,
                image_resolution=task.image_resolution,
            ),
        )

        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
            box_loss="ciou",
            classification_loss="binary_crossentropy",
            jit_compile=False,
        )

    logger.success("Model compiled successfully")
    model.summary()

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
        lr=lr,
        batch_size=batch_size,
        n_epochs=epochs,
        image_resolution=task.image_resolution
    )


    logger.success(f"Training completed. Model saved to {model_filepath}")
