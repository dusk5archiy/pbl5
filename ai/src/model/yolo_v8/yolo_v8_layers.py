import tensorflow as tf
from keras import ops

BATCH_NORM_EPSILON = 1e-3
BATCH_NORM_MOMENTUM = 0.97


def apply_conv_bn(
    inputs,
    output_channel,
    kernel_size=1,
    strides=1,
    activation="swish",
    name="conv_bn",
):
    if kernel_size > 1:
        inputs = tf.keras.layers.ZeroPadding2D(
            padding=kernel_size // 2, name=f"{name}_pad"
        )(inputs)

    x = tf.keras.layers.Conv2D(
        filters=output_channel,
        kernel_size=kernel_size,
        strides=strides,
        use_bias=False,
        name=f"{name}_conv",
    )(inputs)
    x = tf.keras.layers.BatchNormalization(
        momentum=BATCH_NORM_MOMENTUM,
        epsilon=BATCH_NORM_EPSILON,
        name=f"{name}_bn",
    )(x)
    x = tf.keras.layers.Activation(activation, name=name)(x)
    return x


def apply_csp_block(
    inputs,
    channels=-1,
    depth=2,
    shortcut=True,
    expansion=0.5,
    activation="swish",
    name="csp_block",
):
    channel_axis = -1
    channels = channels if channels > 0 else inputs.shape[channel_axis]
    hidden_channels = int(channels * expansion)

    pre = apply_conv_bn(
        inputs,
        hidden_channels * 2,
        kernel_size=1,
        activation=activation,
        name=f"{name}_pre",
    )
    short, deep = ops.split(pre, 2, axis=channel_axis)

    out = [short, deep]
    for id in range(depth):
        deep = apply_conv_bn(
            deep,
            hidden_channels,
            kernel_size=3,
            activation=activation,
            name=f"{name}_pre_{id}_1",
        )
        deep = apply_conv_bn(
            deep,
            hidden_channels,
            kernel_size=3,
            activation=activation,
            name=f"{name}_pre_{id}_2",
        )
        deep = (out[-1] + deep) if shortcut else deep
        out.append(deep)
    out = ops.concatenate(out, axis=channel_axis)
    out = apply_conv_bn(
        out,
        channels,
        kernel_size=1,
        activation=activation,
        name=f"{name}_output",
    )
    return out
