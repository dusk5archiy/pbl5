import numpy as np
import tensorflow as tf
from typing import Iterator, Tuple
from tqdm import tqdm
from src.backend.logging import logger

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

    def generator() -> Iterator[Tuple[np.ndarray, np.ndarray]]:
        for img_array, bboxes in tqdm(iterable):
            if bboxes:
                boxes = np.array(bboxes, dtype=np.float32)
            else:
                boxes = np.zeros((0, 4), dtype=np.float32)
            yield img_array, boxes

    # Collect all data when use_random is False
    if not use_random:
        all_images = []
        all_boxes = []
        
        for img_array, boxes in generator():
            all_images.append(img_array)
            all_boxes.append(boxes)
        
        # Stack images into single array, convert boxes to ragged tensor
        all_images = np.stack(all_images, axis=0)  # Stack into single array
        all_boxes = tf.ragged.constant(all_boxes, ragged_rank=1)  # Ragged for variable length
        ds = tf.data.Dataset.from_tensor_slices((all_images, all_boxes))
    else:
        # Original streaming behavior
        ds = tf.data.Dataset.from_generator(
            generator,
            output_signature=(
                tf.TensorSpec(shape=(img_h, img_w, num_channels), dtype=tf.uint8),
                tf.TensorSpec(shape=(None, 4), dtype=tf.float32),
            ),
        )
    
    # Common preprocessing pipeline for both cases
    ds = ds.map(
        lambda img, boxes: (
            tf.cast(img, tf.float32) / 255.0,
            boxes,
            tf.zeros(tf.shape(boxes)[0], dtype=tf.float32),
        ),
        num_parallel_calls=tf.data.AUTOTUNE,
    )
    
    ds = ds.padded_batch(
        batch_size,
        padded_shapes=(
            tf.TensorShape([img_h, img_w, num_channels]),
            tf.TensorShape([None, 4]),
            tf.TensorShape([None]),
        ),
        padding_values=(0.0, -1.0, -1.0),
    )

    ds = ds.prefetch(tf.data.AUTOTUNE)
    ds = ds.cache()

    def to_model_input(img: tf.Tensor, boxes: tf.Tensor, classes: tf.Tensor):
        valid_mask = tf.reduce_any(boxes != -1.0, axis=-1)
        boxes = tf.ragged.boolean_mask(boxes, valid_mask)
        classes = tf.ragged.boolean_mask(classes, valid_mask)
        return img, {"boxes": boxes, "classes": classes}

    ds = ds.map(to_model_input, num_parallel_calls=tf.data.AUTOTUNE)
    logger.success("Dataset created successfully.")
    return ds