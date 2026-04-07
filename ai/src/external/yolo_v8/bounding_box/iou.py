import math

import tensorflow as tf
from .. import bounding_box
from keras import ops

def compute_ciou(boxes1, boxes2, bounding_box_format):
    target_format = "xyxy"
    if bounding_box.is_relative(bounding_box_format):
        target_format = bounding_box.as_relative(target_format)

    boxes1 = bounding_box.convert_format(
        boxes1, source=bounding_box_format, target=target_format
    )

    boxes2 = bounding_box.convert_format(
        boxes2, source=bounding_box_format, target=target_format
    )

    x_min1, y_min1, x_max1, y_max1 = ops.split(boxes1[..., :4], 4, axis=-1)
    x_min2, y_min2, x_max2, y_max2 = ops.split(boxes2[..., :4], 4, axis=-1)

    width_1 = x_max1 - x_min1
    height_1 = y_max1 - y_min1 + tf.keras.backend.epsilon()
    width_2 = x_max2 - x_min2
    height_2 = y_max2 - y_min2 + tf.keras.backend.epsilon()

    intersection_area = ops.maximum(
        ops.minimum(x_max1, x_max2) - ops.maximum(x_min1, x_min2), 0
    ) * ops.maximum(
        ops.minimum(y_max1, y_max2) - ops.maximum(y_min1, y_min2), 0
    )
    union_area = (
        width_1 * height_1
        + width_2 * height_2
        - intersection_area
        + tf.keras.backend.epsilon()
    )
    iou = ops.squeeze(
        ops.divide(intersection_area, union_area + tf.keras.backend.epsilon()),
        axis=-1,
    )

    convex_width = ops.maximum(x_max1, x_max2) - ops.minimum(x_min1, x_min2)
    convex_height = ops.maximum(y_max1, y_max2) - ops.minimum(y_min1, y_min2)
    convex_diagonal_squared = ops.squeeze(
        convex_width**2 + convex_height**2 + tf.keras.backend.epsilon(),
        axis=-1,
    )
    centers_distance_squared = ops.squeeze(
        ((x_min1 + x_max1) / 2 - (x_min2 + x_max2) / 2) ** 2
        + ((y_min1 + y_max1) / 2 - (y_min2 + y_max2) / 2) ** 2,
        axis=-1,
    )

    v = ops.squeeze(
        ops.power(
            (4 / math.pi**2)
            * (ops.arctan(width_2 / height_2) - ops.arctan(width_1 / height_1)),
            2,
        ),
        axis=-1,
    )
    alpha = v / (v - iou + (1 + tf.keras.backend.epsilon()))

    return iou - (
        centers_distance_squared / convex_diagonal_squared + v * alpha
    )

