import tensorflow as tf

class Rng:
    def __init__(self, seed: int = 42):
        self.generator = tf.random.Generator.from_seed(seed)

    def __call__(self) -> tf.Tensor:
        seed = tf.cast(tf.squeeze(self.generator.make_seeds(1)), tf.int32)
        return tf.reshape(seed, [2])
