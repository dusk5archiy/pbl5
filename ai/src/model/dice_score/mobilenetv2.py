from ..shared.base import BaseAIModel
from ..shared.args import DiceScoreTaskArgs
import tensorflow as tf
from src.composables.prepare_input import prepare_image_input
from src.external.mobilenetv2 import MobileNetV2

class MobilenetV2(BaseAIModel):
    class Config(DiceScoreTaskArgs):
        pass

    def __init__(self, config: Config):
        x, inp = prepare_image_input(
            image_resolution=config.image_resolution,
            n_channels=config.num_channels,
        )
        
        model = MobileNetV2(num_classes=config.num_classes)
        x = model(x)

        tf.keras.Model.__init__(self, inputs=inp, outputs=x)
        BaseAIModel.__init__(self, config)

