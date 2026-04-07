import tensorflow as tf
import keras
from src.model.shared.args import DiceScoreTaskArgs
from src.model.shared.base import BaseAIModel

class MobileNet(BaseAIModel):
    class Config(DiceScoreTaskArgs):
        dense_dim: int
        dropout: float
    
    def __init__(self, config: Config):
        inp = tf.keras.layers.Input(shape=(*config.image_resolution, config.num_channels))
        
        if config.num_channels == 1:
            x = tf.keras.layers.Concatenate(axis=-1)([inp, inp, inp])
        else:
            x = inp
        
        base_model = keras.applications.MobileNetV3Small(
            include_top=False,
            pooling="avg"
        )
        
        x = base_model(x)
        x = tf.keras.layers.Dense(config.dense_dim, activation='relu')(x)
        x = tf.keras.layers.Dropout(config.dropout)(x)
        x = tf.keras.layers.Dense(config.num_classes, activation='softmax')(x)
        
        super().__init__(inputs=inp, outputs=x)