import tensorflow as tf

from . import validate_format
from .. import backend


def to_ragged(bounding_boxes, sentinel=-1, dtype=tf.float32):
    if backend.supports_ragged() is False:
        raise NotImplementedError(
            "`bounding_box.to_ragged` was called using a backend which does "
            "not support ragged tensors. "
            f"Current backend: {tf.keras.backend.backend()}."
        )

    info = validate_format.validate_format(bounding_boxes)

    if info["ragged"]:
        return bounding_boxes

    boxes = bounding_boxes.get("boxes")
    classes = bounding_boxes.get("classes")
    confidence = bounding_boxes.get("confidence", None)

    mask = classes != sentinel

    boxes = tf.ragged.boolean_mask(boxes, mask)
    classes = tf.ragged.boolean_mask(classes, mask)
    if confidence is not None:
        confidence = tf.ragged.boolean_mask(confidence, mask)

    if isinstance(boxes, tf.Tensor):
        boxes = tf.RaggedTensor.from_tensor(boxes)

    if isinstance(classes, tf.Tensor) and len(classes.shape) > 1:
        classes = tf.RaggedTensor.from_tensor(classes)

    if confidence is not None:
        if isinstance(confidence, tf.Tensor) and len(confidence.shape) > 1:
            confidence = tf.RaggedTensor.from_tensor(confidence)

    result = bounding_boxes.copy()
    result["boxes"] = tf.cast(boxes, dtype)
    result["classes"] = tf.cast(classes, dtype)

    if confidence is not None:
        result["confidence"] = tf.cast(confidence, dtype)

    return result

