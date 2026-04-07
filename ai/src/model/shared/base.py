import tensorflow as tf
from pydantic import BaseModel

class BaseAIModel(tf.keras.Model):
    class Config(BaseModel):
        pass

    @classmethod
    def from_config(cls, config):
        result =  cls(config=cls.Config(**config))
        return result