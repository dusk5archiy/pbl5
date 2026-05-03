import numpy as np
import tensorflow as tf

class DotKerasInference:
    def __init__(self, model_path: str):
        self.model = tf.keras.models.load_model(model_path)

    @tf.function(reduce_retracing=True)
    def _inference(self, x):
        if x.shape.rank == 3:
            x = x[None, ...]

        return self.model(x, training=False)

    def __call__(self, x):
        pred = self._inference(x)
        class_idx = int(np.argmax(pred[0]))

        return class_idx
