import numpy as np
import tensorflow as tf

def make_tf_dataset(iterable, batch_size: int, image_resolution: tuple[int, int], colored: bool):
    '''
    The `iterable` must yield tuple[np.ndarray, list[tuple[int, int, int, int]]].
    '''
    img_w, img_h = image_resolution
    num_channels = 3 if colored else 1
    def generator():
        for img_array, bboxes in iterable:
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
            tf.TensorSpec(shape=(img_h, img_w, num_channels), dtype=tf.float32),
            tf.TensorSpec(shape=(None, 4), dtype=tf.float32),
            tf.TensorSpec(shape=(None, ), dtype=tf.float32),
        ),
    ).padded_batch(
        batch_size,
        padded_shapes=([img_h, img_w, num_channels], [None, 4], [None]), # type: ignore
        padding_values=(0.0, -1.0, -1.0),
    )
    
    def to_model_input(img, boxes, classes):
        valid_mask = tf.reduce_any(boxes != -1.0, axis=-1)  # [B, N]
        boxes = tf.ragged.boolean_mask(boxes, valid_mask)
        classes = tf.ragged.boolean_mask(classes, valid_mask)
        return img, {"boxes": boxes, "classes": classes}

    return ds.map(to_model_input, num_parallel_calls=tf.data.AUTOTUNE)
