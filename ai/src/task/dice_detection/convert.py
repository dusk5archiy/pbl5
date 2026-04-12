import tensorflow as tf
from src.backend.logging import logger
from pathlib import Path
from src.dataset import (
    S7DatasetDiceDetection,
    get_image_detection_datas,
)

from src.dataset.dice_detection.tf import make_tf_dataset

def convert2_tflite(
        path: str,
        image_resolution: tuple[int, int],
        colored: bool=True,
        quantization: str = "float16",
        dataset_path: str | None = None,
        num_workers: int = 4
    ):
    num_channels = 3 if colored else 1
    logger.info("Importing model...")
    from src.model.dice_detection.yolov8 import YoloV8

    model = tf.keras.models.load_model(
        path,
        custom_objects={"YoloV8": YoloV8},
    )
    logger.info("Converting...")

    @tf.function(input_signature=[
        tf.TensorSpec(shape=[1, image_resolution[1], image_resolution[0], num_channels], dtype=tf.float32)
    ])
    def run_model(x):
        return model(x, training=False)
    
    concrete_func = run_model.get_concrete_function()
    converter = tf.lite.TFLiteConverter.from_concrete_functions([concrete_func])
    
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    
    if quantization == "int8":
        # INT8 full quantization requires representative dataset
        if dataset_path is None:
            logger.warning("INT8 quantization requires dataset_path. Using dynamic quantization instead.")
            converter.target_spec.supported_types = [tf.int8, tf.float32]
        else:
            logger.info(f"Creating representative dataset from {dataset_path}...")
            
            # Reuse same dataset loading as training
            calibration_datas = get_image_detection_datas(
                dataset_path=dataset_path, num_workers=num_workers
            )
            calibration_iterable = S7DatasetDiceDetection(
                image_resolution=image_resolution,
                image_datas=calibration_datas,
                cache_path="output/dice_detection_train",
                num_workers=num_workers,
                colored=colored,
                use_random=False
            )
            
            # Create dataset with batch size 1 for representative samples
            calibration_dataset = make_tf_dataset(
                calibration_iterable,
                batch_size=1,
                image_resolution=image_resolution,
                colored=colored,
                use_random=False
            )
            
            def representative_dataset():
                for img_batch, _ in calibration_dataset.take(1):
                    yield [img_batch]
            
            converter.representative_dataset = representative_dataset
            converter.target_spec.supported_types = [tf.int8]
            
    elif quantization == "float16":
        converter.target_spec.supported_types = [tf.float16]
    
    logger.info(f"Using {quantization} quantization...")
    tflite_model = converter.convert()
    
    output_path = Path(path).with_suffix('.tflite')
    with open(output_path, 'wb') as f:
        f.write(tflite_model)
    
    logger.success(f"Detection model converted to {output_path}.")