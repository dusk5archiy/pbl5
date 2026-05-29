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

from pydantic import validate_call
from tqdm.keras import TqdmCallback
import tensorflow as tf
from keras import mixed_precision

from datetime import datetime
import os

@validate_call
def train_savedmodel(
    model_name: str,
    config: ParsedConfig,
    batch_size: int,
    lr: float,
    epochs: int,
    task: ParsedConfig.Tasks.DiceScore,
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

    # Initialize MirroredStrategy
    strategy = tf.distribute.MirroredStrategy()
    logger.info(f"Number of devices in strategy: {strategy.num_replicas_in_sync}")

    # For classification JIT usually works, but following "similar to detection" pattern
    tf.config.optimizer.set_jit(False)

    train_dataset, val_dataset = load_dataset(
        config=config,
        batch_size=batch_size,
        task=task,
    )

    with strategy.scope():
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
            optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
            jit_compile=False,
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
        lr=lr,
        model_name=model_name,
        batch_size=batch_size,
        n_epochs=epochs,
        image_resolution=task.image_resolution,
    )

    logger.success(f"Training completed. Model saved to {model_filepath}")
