import tensorflow as tf
from keras import ops
from .yolo_v8_layers import apply_conv_bn, apply_csp_block

BOX_REGRESSION_CHANNELS = 64


def get_anchors(
    image_shape,
    strides=[8, 16, 32],
    base_anchors=[0.5, 0.5],
):
    base_anchors = ops.array(base_anchors, dtype="float32")

    all_anchors = []
    all_strides = []
    for stride in strides:
        hh_centers = ops.arange(0, image_shape[0], stride)
        ww_centers = ops.arange(0, image_shape[1], stride)
        ww_grid, hh_grid = ops.meshgrid(ww_centers, hh_centers)
        grid = ops.cast(
            ops.reshape(ops.stack([hh_grid, ww_grid], 2), [-1, 1, 2]),
            "float32",
        )
        anchors = (
            ops.expand_dims(
                base_anchors * ops.array([stride, stride], "float32"), 0
            )
            + grid
        )
        anchors = ops.reshape(anchors, [-1, 2])
        all_anchors.append(anchors)
        all_strides.append(ops.repeat(stride, anchors.shape[0]))

    all_anchors = ops.cast(ops.concatenate(all_anchors, axis=0), "float32")
    all_strides = ops.cast(ops.concatenate(all_strides, axis=0), "float32")

    all_anchors = all_anchors / all_strides[:, None]

    # Swap the x and y coordinates of the anchors.
    all_anchors = ops.concatenate(
        [all_anchors[:, 1, None], all_anchors[:, 0, None]], axis=-1
    )
    return all_anchors, all_strides


def apply_path_aggregation_fpn(features, depth=3, name="fpn"):
    p3, p4, p5 = features

    # Upsample P5 and concatenate with P4, then apply a CSPBlock.
    p5_upsampled = ops.repeat(ops.repeat(p5, 2, axis=1), 2, axis=2)
    p4p5 = ops.concatenate([p5_upsampled, p4], axis=-1)
    p4p5 = apply_csp_block(
        p4p5,
        channels=p4.shape[-1],
        depth=depth,
        shortcut=False,
        activation="swish",
        name=f"{name}_p4p5",
    )

    # Upsample P4P5 and concatenate with P3, then apply a CSPBlock.
    p4p5_upsampled = ops.repeat(ops.repeat(p4p5, 2, axis=1), 2, axis=2)
    p3p4p5 = ops.concatenate([p4p5_upsampled, p3], axis=-1)
    p3p4p5 = apply_csp_block(
        p3p4p5,
        channels=p3.shape[-1],
        depth=depth,
        shortcut=False,
        activation="swish",
        name=f"{name}_p3p4p5",
    )

    # Downsample P3P4P5, concatenate with P4P5, and apply a CSP Block.
    p3p4p5_d1 = apply_conv_bn(
        p3p4p5,
        p3p4p5.shape[-1],
        kernel_size=3,
        strides=2,
        activation="swish",
        name=f"{name}_p3p4p5_downsample1",
    )
    p3p4p5_d1 = ops.concatenate([p3p4p5_d1, p4p5], axis=-1)
    p3p4p5_d1 = apply_csp_block(
        p3p4p5_d1,
        channels=p4p5.shape[-1],
        shortcut=False,
        activation="swish",
        name=f"{name}_p3p4p5_downsample1_block",
    )

    # Downsample the resulting P3P4P5 again, concatenate with P5, and apply
    # another CSP Block.
    p3p4p5_d2 = apply_conv_bn(
        p3p4p5_d1,
        p3p4p5_d1.shape[-1],
        kernel_size=3,
        strides=2,
        activation="swish",
        name=f"{name}_p3p4p5_downsample2",
    )
    p3p4p5_d2 = ops.concatenate([p3p4p5_d2, p5], axis=-1)
    p3p4p5_d2 = apply_csp_block(
        p3p4p5_d2,
        channels=p5.shape[-1],
        shortcut=False,
        activation="swish",
        name=f"{name}_p3p4p5_downsample2_block",
    )

    return [p3p4p5, p3p4p5_d1, p3p4p5_d2]


def apply_yolo_v8_head(
    inputs,
    num_classes,
    name="yolo_v8_head",
):
    # 64 is the default number of channels, as 16 components are used to predict
    # each of the 4 offsets for corner points of a bounding box with respect
    # to the center point. In cases where the input has much higher resolution
    # (e.g. the P3 input has >256 channels), we use additional channels for
    # the intermediate conv layers. This is only true for very large backbones.
    box_channels = max(BOX_REGRESSION_CHANNELS, inputs[0].shape[-1] // 4)

    # We use at least num_classes channels for intermediate conv layer for class
    # predictions. In most cases, the P3 input has many more channels than the
    # number of classes, so we preserve those channels until the final layer.
    class_channels = max(num_classes, inputs[0].shape[-1])

    # We compute box and class predictions for each of the feature maps from
    # the FPN and then combine them.
    outputs = []
    for id, feature in enumerate(inputs):
        cur_name = f"{name}_{id+1}"

        box_predictions = apply_conv_bn(
            feature,
            box_channels,
            kernel_size=3,
            activation="swish",
            name=f"{cur_name}_box_1",
        )
        box_predictions = apply_conv_bn(
            box_predictions,
            box_channels,
            kernel_size=3,
            activation="swish",
            name=f"{cur_name}_box_2",
        )
        box_predictions = tf.keras.layers.Conv2D(
            filters=BOX_REGRESSION_CHANNELS,
            kernel_size=1,
            name=f"{cur_name}_box_3_conv",
        )(box_predictions)

        class_predictions = apply_conv_bn(
            feature,
            class_channels,
            kernel_size=3,
            activation="swish",
            name=f"{cur_name}_class_1",
        )
        class_predictions = apply_conv_bn(
            class_predictions,
            class_channels,
            kernel_size=3,
            activation="swish",
            name=f"{cur_name}_class_2",
        )
        class_predictions = tf.keras.layers.Conv2D(
            filters=num_classes,
            kernel_size=1,
            name=f"{cur_name}_class_3_conv",
        )(class_predictions)
        class_predictions = tf.keras.layers.Activation(
            "sigmoid", name=f"{cur_name}_classifier"
        )(class_predictions)

        out = ops.concatenate([box_predictions, class_predictions], axis=-1)
        out = tf.keras.layers.Reshape(
            [-1, out.shape[-1]], name=f"{cur_name}_output_reshape"
        )(out)
        outputs.append(out)

    outputs = ops.concatenate(outputs, axis=1)
    outputs = tf.keras.layers.Activation(
        "linear", dtype="float32", name="box_outputs"
    )(outputs)

    return {
        "boxes": outputs[:, :, :BOX_REGRESSION_CHANNELS],
        "classes": outputs[:, :, BOX_REGRESSION_CHANNELS:],
    }


def decode_regression_to_boxes(preds):
    preds_bbox = tf.keras.layers.Reshape((-1, 4, BOX_REGRESSION_CHANNELS // 4))(preds)
    preds_bbox = ops.nn.softmax(preds_bbox, axis=-1) * ops.arange(
        BOX_REGRESSION_CHANNELS // 4, dtype="float32"
    )
    out = ops.sum(preds_bbox, axis=-1)
    return out


def dist2bbox(distance, anchor_points):
    left_top, right_bottom = ops.split(distance, 2, axis=-1)
    x1y1 = anchor_points - left_top
    x2y2 = anchor_points + right_bottom
    return ops.concatenate((x1y1, x2y2), axis=-1)  # xyxy bbox

