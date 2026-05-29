from src.backend.logging import logger
from src.dataset.dice_score.custom_dice_dataset import CustomDiceScoreDataset

import tensorflow as tf

from pathlib import Path

def convert2_tflite(
    path: str,
    image_resolution: tuple[int, int] = (32, 32),
    quantization: str = "float16",
    dataset_path: str | None = None,
    colored: bool = True,
):
    num_channels = 3 if colored else 1
    logger.info("Importing model...")
    model = tf.keras.models.load_model(path)

    logger.info("Converting...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    if quantization == "int8":
        # INT8 full quantization requires representative dataset
        if dataset_path is None:
            logger.warning(
                "INT8 quantization requires dataset_path. Using dynamic quantization instead."
            )
            converter.target_spec.supported_types = [tf.int8, tf.float32]
        else:
            logger.info(f"Creating representative dataset from {dataset_path}...")

            # Use CustomDataset manager
            dataset_manager = CustomDiceScoreDataset(
                root_dir=dataset_path,
                image_size=image_resolution,
                colored=colored,
                seed=42
            )

            # Get base dataset (contains image and label)
            # Batch size 1 required for representative dataset
            calibration_dataset = dataset_manager.get_tf_dataset(base_only=True).batch(1)

            def representative_dataset():
                for img_batch, _ in calibration_dataset.take(100):  # Use up to 100 batches
                    yield [img_batch]

            converter.representative_dataset = representative_dataset
            converter.target_spec.supported_types = [tf.int8]

    elif quantization == "float16":
        converter.target_spec.supported_types = [tf.float16]

    logger.info(f"Using {quantization} quantization...")
    tflite_model = converter.convert()

    output_path = Path(path).with_suffix('.tflite')
    with open(output_path, "wb") as f:
        f.write(tflite_model)

    logger.success(f"Score model converted to {output_path}")

