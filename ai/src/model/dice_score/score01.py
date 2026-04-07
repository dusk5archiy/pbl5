import tensorflow as tf
from src.model.shared.args import DiceScoreTaskArgs
from src.model.shared.base import BaseAIModel
from pydantic import Field
from typing import Literal

class Score01(BaseAIModel):
    class Config(DiceScoreTaskArgs):
        filter_list: list[int] = Field(min_length=1)
        dense_dim: int
        activation: str
        dropout: float
        padding: Literal["valid", "same"] = "same"

    def __init__(self, config: Config):
        filter_list = config.filter_list

        inp = tf.keras.layers.Input(shape=(*config.image_resolution, config.num_channels))
        x = tf.keras.layers.Conv2D(
            filter_list[0],
            3,
            padding=config.padding,
            activation=config.activation,
        )(inp)
        for filter in filter_list[1:]:
            x = tf.keras.layers.MaxPooling2D(2, 2)(x)
            x = tf.keras.layers.Conv2D(
                filter,
                3,
                padding=config.padding,
                activation=config.activation,
            )(x)
        x = tf.keras.layers.Flatten()(x)
        x = tf.keras.layers.Dense(config.dense_dim, activation=config.activation)(x)
        x = tf.keras.layers.Dropout(config.dropout)(x)
        x = tf.keras.layers.Dense(config.num_classes, activation='softmax')(x)
        super().__init__(inputs=inp, outputs=x)