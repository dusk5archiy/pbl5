import tensorflow as tf
from pydantic import BaseModel

class BaseAIModel(tf.keras.Model):
    class Config:
        pass
    def __init__(self, config: BaseModel):
        self.config = config
        
    @classmethod
    def from_config(cls, config):
        return cls(config=cls.Config(**config))
    
    def get_config(self):
        return self.config.model_dump()