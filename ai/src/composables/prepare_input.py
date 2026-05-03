import tensorflow as tf
from src.types import T_IMAGE_RESOLUTION

layers = tf.keras.layers

def prepare_image_input(
    image_resolution: T_IMAGE_RESOLUTION,
    n_channels: int,
) -> tuple:
    x = inp = tf.keras.layers.Input(
        shape=(
            image_resolution[1],
            image_resolution[0],
            n_channels,
        )
    )
    
    if n_channels == 1:
        x = layers.Concatenate(axis=-1)([inp, inp, inp])
    else:
        x = inp
        
    return x, inp