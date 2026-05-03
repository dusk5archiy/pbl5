from src.backend.logging import logger
from src.dataset import S7DatasetDiceScore, get_dice_crops

import tensorflow as tf

from pathlib import Path

def convert2_tflite(
    path: str,
    image_resolution: tuple[int, int] = (32, 32),
    quantization: str = "float16",
    dataset_path: str | None = None,
    colored: bool = True,
    num_workers: int = 4,
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

            # Reuse same dataset loading as training
            all_dice_crops = get_dice_crops(
                dataset_path=dataset_path,
                num_workers=num_workers,
            )

            calibration_crops = all_dice_crops[: max(1, len(all_dice_crops) // 5)]

            calibration_dataset_obj = S7DatasetDiceScore(
                image_resolution=image_resolution,
                dice_crops=calibration_crops,
                colored=colored,
                use_random=True
            )

            # Create generator similar to training
            def calibration_generator():
                for img, _ in calibration_dataset_obj:
                    yield tf.cast(img, tf.float32) / 255.0

            shape = (*image_resolution, num_channels)
            calibration_dataset = tf.data.Dataset.from_generator(
                calibration_generator,
                output_signature=tf.TensorSpec(shape=shape, dtype=tf.float32),
            ).batch(batch_size=1)

            def representative_dataset():
                for img_batch in calibration_dataset.take(100):  # Use up to 100 batches
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

