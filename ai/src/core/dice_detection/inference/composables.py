from ..utils import decode_dfl

import tensorflow as tf


@tf.function(reduce_retracing=True)
def process_predictions(
    preds,
    image_resolution,
    conf_threshold: float,
    iou_threshold: float,
):
    # Decode and squeeze
    boxes = decode_dfl(preds["boxes"][0], image_resolution)
    confs = tf.squeeze(preds["classes"][0])

    # Filter by confidence
    mask = confs > conf_threshold
    boxes = boxes[mask]
    confs = confs[mask]

    # Apply NMS
    def empty_case():
        return tf.zeros((0, 4), dtype=tf.float32)

    def non_empty_case():
        indices = tf.image.non_max_suppression(
            boxes,
            confs,
            max_output_size=10,
            iou_threshold=iou_threshold,
        )
        return tf.gather(boxes, indices)

    return tf.cond(tf.equal(tf.shape(boxes)[0], 0), empty_case, non_empty_case)
