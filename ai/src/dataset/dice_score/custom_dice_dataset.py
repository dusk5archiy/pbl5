import os
import tensorflow as tf
import numpy as np
from src.common.rng import Rng
from src.common.augment import brightness_contrast, add_noise, blur

class CustomDiceScoreDataset:
    def __init__(self, root_dir, image_size, colored, seed=42):
        self.root_dir = root_dir
        self.image_size = image_size
        self.colored = colored
        self.seed = seed
        self.np_rng = np.random.default_rng(seed)
        self.rng = Rng(seed)
        
        self.input_dir = os.path.join(root_dir, "inputs")
        self.target_dir = os.path.join(root_dir, "targets")
        
        self.samples = []
        if os.path.exists(self.target_dir):
            for root, _, files in os.walk(self.target_dir):
                for file in files:
                    if file.endswith(".txt"):
                        target_path = os.path.join(root, file)
                        rel_path = os.path.relpath(target_path, self.target_dir)
                        input_rel_path = rel_path.replace(".txt", ".png")
                        input_path = os.path.join(self.input_dir, input_rel_path)
                        
                        if os.path.exists(input_path):
                            try:
                                with open(target_path, "r") as f:
                                    for line in f:
                                        parts = line.strip().split()
                                        if len(parts) >= 5:
                                            # x, y, w, h, score
                                            x, y, w, h, score = map(int, parts[:5])
                                            # Filter out invalid crops
                                            if w > 0 and h > 0:
                                                self.samples.append({
                                                    "path": input_path,
                                                    "crop": [y, x, h, w], # [y_min, x_min, height, width] for tf.image.crop_to_bounding_box
                                                    "label": score - 1    # 0-5 for classification
                                                })
                            except Exception:
                                pass
        
        self.np_rng.shuffle(self.samples)

    def __len__(self):
        return len(self.samples)

    @property
    def num_classes(self):
        return 6

    def apply_augmentation(self, img, label):
        # Classification-only augmentations
        # Rotation (90 deg increments)
        k = tf.random.stateless_uniform([], seed=self.rng(), minval=0, maxval=4, dtype=tf.int32)
        img = tf.image.rot90(img, k=k)
        
        # Flips
        if tf.random.stateless_uniform([], seed=self.rng()) > 0.5:
            img = tf.image.flip_left_right(img)
        if tf.random.stateless_uniform([], seed=self.rng()) > 0.5:
            img = tf.image.flip_up_down(img)
            
        img = brightness_contrast(img, self.rng)
        img = add_noise(img, self.rng)
        img = blur(img, self.rng)
        return img, label

    def format_output(self, img, label):
        img_w, img_h = self.image_size
        img.set_shape([img_h, img_w, 3 if self.colored else 1])
        return (img, label)

    def get_tf_dataset(
        self,
        augment: bool = False,
        repeat: int = 1,
        base_only: bool = False,
        cache_path: str | None = None,
    ):
        channels = 3 if self.colored else 1
        img_w, img_h = self.image_size

        def load_sample(path, crop, label):
            img = tf.io.read_file(path)
            img = tf.image.decode_png(img, channels=channels)
            
            # Crop to the dice
            y, x, h, w = crop[0], crop[1], crop[2], crop[3]
            img = tf.image.crop_to_bounding_box(img, y, x, h, w)
            
            # Resize to model input size
            img = tf.image.resize(img, [img_h, img_w])
            img = tf.cast(img, tf.float32) / 255.0
            
            return img, label

        # Extract lists for tensor slices
        paths = [s["path"] for s in self.samples]
        crops = [s["crop"] for s in self.samples]
        labels = [s["label"] for s in self.samples]
        
        dataset = tf.data.Dataset.from_tensor_slices((
            tf.constant(paths, dtype=tf.string),
            tf.constant(crops, dtype=tf.int32),
            tf.constant(labels, dtype=tf.int32)
        ))
        
        dataset = dataset.map(load_sample, num_parallel_calls=tf.data.AUTOTUNE)

        if cache_path:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            dataset = dataset.cache(cache_path)

        if base_only:
            return dataset

        dataset = dataset.repeat(repeat)
        if augment:
            dataset = dataset.map(self.apply_augmentation, num_parallel_calls=tf.data.AUTOTUNE)

        dataset = dataset.map(self.format_output, num_parallel_calls=tf.data.AUTOTUNE)
        dataset = dataset.prefetch(tf.data.AUTOTUNE)
        return dataset
