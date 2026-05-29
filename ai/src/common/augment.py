import tensorflow as tf
from src.common.rng import Rng

def brightness_contrast(img, rng: Rng):
    img = tf.image.stateless_random_brightness(img, max_delta=0.1, seed=rng())
    img = tf.image.stateless_random_contrast(img, lower=0.9, upper=1.1, seed=rng())
    return img

def blur(img, rng: Rng):
    if tf.random.stateless_uniform([], seed=rng()) > 0.5:
        img = tf.expand_dims(img, 0)
        img = tf.nn.avg_pool2d(img, ksize=3, strides=1, padding='SAME')
        img = tf.squeeze(img, 0)
    return img

def add_noise(img, rng: Rng):
    noise = tf.random.stateless_normal(shape=tf.shape(img), mean=0.0, stddev=0.02, seed=rng())
    img = img + noise
    img = tf.clip_by_value(img, 0.0, 1.0)
    return img

def rotate(img, bboxes, rng: Rng):
    shape = tf.shape(img)
    img_h, img_w = tf.cast(shape[0], tf.float32), tf.cast(shape[1], tf.float32)
    if img_w == img_h:
        k = tf.random.stateless_uniform([], seed=rng(), minval=0, maxval=4, dtype=tf.int32)
    else:
        k = tf.random.stateless_uniform([], seed=rng(), minval=0, maxval=2, dtype=tf.int32) * 2

    img = tf.image.rot90(img, k=k)
    
    if tf.shape(bboxes)[0] > 0:
        def rot90():
            x, y, w, h = [bboxes[:, i] for i in range(4)]
            return tf.stack([y, img_w - x - w, h, w], axis=-1)
        def rot180():
            x, y, w, h = [bboxes[:, i] for i in range(4)]
            return tf.stack([img_w - x - w, img_h - y - h, w, h], axis=-1)
        def rot270():
            x, y, w, h = [bboxes[:, i] for i in range(4)]
            return tf.stack([img_h - y - h, x, h, w], axis=-1)

        bboxes = tf.case([
            (tf.equal(k, 1), rot90),
            (tf.equal(k, 2), rot180),
            (tf.equal(k, 3), rot270)
        ], default=lambda: bboxes)
        
    return img, bboxes

def flip(img, bboxes, rng: Rng):
    shape = tf.shape(img)
    img_h, img_w = tf.cast(shape[0], tf.float32), tf.cast(shape[1], tf.float32)

    if tf.random.stateless_uniform([], seed=rng()) > 0.5:
        img = tf.image.flip_left_right(img)
        if tf.shape(bboxes)[0] > 0:
            x, y, w, h = [bboxes[:, i] for i in range(4)]
            x = img_w - x - w
            bboxes = tf.stack([x, y, w, h], axis=-1)

    if tf.random.stateless_uniform([], seed=rng()) > 0.5:
        img = tf.image.flip_up_down(img)
        if tf.shape(bboxes)[0] > 0:
            x, y, w, h = [bboxes[:, i] for i in range(4)]
            y = img_h - y - h
            bboxes = tf.stack([x, y, w, h], axis=-1)
            
    return img, bboxes