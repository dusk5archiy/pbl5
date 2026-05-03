from src.backend.logging import logger

from tqdm import tqdm
import numpy as np
import tensorflow as tf

from typing import Iterator, Tuple


def make_tf_dataset(
    iterable,
    batch_size: int,
    image_resolution: tuple[int, int],
    colored: bool,
    use_random: bool,
) -> tf.data.Dataset:
    logger.info("Creating dataset...")
    img_w, img_h = image_resolution
    num_channels = 3 if colored else 1

    def generator() -> Iterator[Tuple[np.ndarray, int]]:
        for img_array, label in tqdm(iterable):
            yield img_array, label

    # Collect all data when use_random is False
    if not use_random:
        all_images = []
        all_labels = []
        
        for img_array, label in generator():
            all_images.append(img_array)
            all_labels.append(label)
        
        # Stack images into single array, convert labels to array
        logger.info("Creating dataset from tensor slices.")
        all_images = np.stack(all_images, axis=0)  # Stack into single array
        all_labels = np.array(all_labels, dtype=np.int32)  # Convert to numpy array
        ds = tf.data.Dataset.from_tensor_slices((all_images, all_labels))
    else:
        # Original streaming behavior
        ds = tf.data.Dataset.from_generator(
            generator,
            output_signature=(
                tf.TensorSpec(shape=(img_h, img_w, num_channels), dtype=tf.uint8),
                tf.TensorSpec(shape=(), dtype=tf.int32),
            ),
        )
    
    # Common preprocessing pipeline for both cases
    ds = ds.map(
        lambda img, label: (
            tf.cast(img, tf.float32) / 255.0,
            label,
        ),
        num_parallel_calls=tf.data.AUTOTUNE,
    )
    
    ds = ds.batch(batch_size)
    ds = ds.prefetch(tf.data.AUTOTUNE)
    ds = ds.cache()

    logger.success("Dataset created successfully.")
    return ds
