import random
import numpy as np
import tensorflow as tf

def enable_determ():
    random.seed(42)
    np.random.seed(42)
    tf.random.set_seed(42)
    tf.config.experimental.enable_op_determinism()