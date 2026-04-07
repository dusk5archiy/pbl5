import tensorflow as tf
from .backend.config import keras_3


def get_tensor_input_name(tensor):
    if keras_3():
        return tensor._keras_history.operation.name
    else:
        return tensor.node.layer.name


def parse_model_inputs(input_shape, input_tensor, **kwargs):
    if input_tensor is None:
        return tf.keras.layers.Input(shape=input_shape, **kwargs)
    else:
        if not tf.keras.backend.is_keras_tensor(input_tensor):
            return tf.keras.layers.Input(
                tensor=input_tensor, shape=input_shape, **kwargs
            )
        else:
            return input_tensor