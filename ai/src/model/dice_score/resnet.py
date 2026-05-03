from ..shared.base import BaseAIModel
from ..shared.args import DiceScoreTaskArgs
import tensorflow as tf
from src.external.resnet import ResNet
from src.composables.prepare_input import prepare_image_input

from typing import Literal

layers = tf.keras.layers

class Resnet(BaseAIModel):
    class Config(DiceScoreTaskArgs):
        model_type: str = Literal["resnet18", "resnet34", "resnet50", "resnet101", "resnet152"]

    def __init__(self, config: Config):
        x, inp = prepare_image_input(
            image_resolution=config.image_resolution,
            n_channels=config.num_channels,
        )

        model = ResNet(config.model_type, config.num_classes)
        x = model(x)

        tf.keras.Model.__init__(self, inputs=inp, outputs=x)
        BaseAIModel.__init__(self, config)

