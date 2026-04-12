import keras
from .backbone import Backbone
import tensorflow as tf
from keras import ops
from . import utils
from .yolo_v8_layers import (
    apply_conv_bn,
    apply_csp_block,
)

def apply_spatial_pyramid_pooling_fast(
    inputs, pool_size=5, activation="swish", name="spp_fast"
):
    channel_axis = -1
    input_channels = inputs.shape[channel_axis]
    hidden_channels = int(input_channels // 2)

    x = apply_conv_bn(
        inputs,
        hidden_channels,
        kernel_size=1,
        activation=activation,
        name=f"{name}_pre",
    )
    pool_1 = tf.keras.layers.MaxPooling2D(
        pool_size=pool_size, strides=1, padding="same", name=f"{name}_pool1"
    )(x)
    pool_2 = tf.keras.layers.MaxPooling2D(
        pool_size=pool_size, strides=1, padding="same", name=f"{name}_pool2"
    )(pool_1)
    pool_3 = tf.keras.layers.MaxPooling2D(
        pool_size=pool_size, strides=1, padding="same", name=f"{name}_pool3"
    )(pool_2)

    out = ops.concatenate([x, pool_1, pool_2, pool_3], axis=channel_axis)
    out = apply_conv_bn(
        out,
        input_channels,
        kernel_size=1,
        activation=activation,
        name=f"{name}_output",
    )
    
    return out

class YOLOV8Backbone(Backbone):
    def __init__(
        self,
        stackwise_channels,
        stackwise_depth,
        include_rescaling,
        activation="swish",
        input_shape=(None, None, 3),
        input_tensor=None,
        **kwargs,
    ):
        inputs = utils.parse_model_inputs(input_shape, input_tensor)

        x = inputs
        if include_rescaling:
            x = tf.keras.layers.Rescaling(1 / 255.0)(x)

        """ Stem """
        stem_width = stackwise_channels[0]
        x = apply_conv_bn(
            x,
            stem_width // 2,
            kernel_size=3,
            strides=2,
            activation=activation,
            name="stem_1",
        )
        x = apply_conv_bn(
            x,
            stem_width,
            kernel_size=3,
            strides=2,
            activation=activation,
            name="stem_2",
        )

        """ blocks """
        pyramid_level_inputs = {"P1": utils.get_tensor_input_name(x)}
        for stack_id, (channel, depth) in enumerate(
            zip(stackwise_channels, stackwise_depth)
        ):
            stack_name = f"stack{stack_id + 1}"
            if stack_id >= 1:
                x = apply_conv_bn(
                    x,
                    channel,
                    kernel_size=3,
                    strides=2,
                    activation=activation,
                    name=f"{stack_name}_downsample",
                )
            x = apply_csp_block(
                x,
                depth=depth,
                expansion=0.5,
                activation=activation,
                name=f"{stack_name}_c2f",
            )

            if stack_id == len(stackwise_depth) - 1:
                x = apply_spatial_pyramid_pooling_fast(
                    x,
                    pool_size=5,
                    activation=activation,
                    name=f"{stack_name}_spp_fast",
                )
            pyramid_level_inputs[f"P{stack_id + 2}"] = (
                utils.get_tensor_input_name(x)
            )

        super().__init__(inputs=inputs, outputs=x, **kwargs)
        self.pyramid_level_inputs = pyramid_level_inputs
        self.stackwise_channels = stackwise_channels
        self.stackwise_depth = stackwise_depth
        self.include_rescaling = include_rescaling
        self.activation = activation

    def get_config(self):
        config = super().get_config()
        config.update(
            {
                "include_rescaling": self.include_rescaling,
                # Remove batch dimension from `input_shape`
                "input_shape": self.input_shape[1:],
                "stackwise_channels": self.stackwise_channels,
                "stackwise_depth": self.stackwise_depth,
                "activation": self.activation,
            }
        )
        return config