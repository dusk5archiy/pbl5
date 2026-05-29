import os
import tensorflow as tf
import numpy as np
from src.common.rng import Rng
from src.common.augment import rotate, flip, add_noise, brightness_contrast, blur

class CustomDiceDataset:

    def __init__(
        self,
        root_dir,
        image_size: tuple[int, int], # width, height
        colored: bool,
        seed=42,
    ):
        self.root_dir = root_dir
        self.seed = seed
        self.np_rng = np.random.default_rng(seed)
        self.rng = Rng(seed)

        self.input_dir = os.path.join(root_dir, "inputs")
        self.target_dir = os.path.join(root_dir, "targets")

        self.image_size = image_size
        self.colored = colored

        self.samples = []
        if os.path.exists(self.target_dir):
            # The dataset structure is nested: targets/{folder}/{file}.txt
            for root, dirs, files in os.walk(self.target_dir):
                for file in files:
                    if file.endswith(".txt"):
                        target_path = os.path.join(root, file)

                        # Calculate relative path from target_dir to get the folder structure
                        rel_path = os.path.relpath(target_path, self.target_dir)
                        input_rel_path = rel_path.replace(".txt", ".png")
                        input_path = os.path.join(self.input_dir, input_rel_path)

                        if os.path.exists(input_path):
                            bboxes = []
                            try:
                                with open(target_path, "r") as f:
                                    for line in f:
                                        parts = line.strip().split()
                                        if len(parts) >= 4:
                                            bboxes.append([float(p) for p in parts[:4]])
                            except Exception:
                                pass

                            if not bboxes:
                                continue # Skip background images if they have no boxes
                            else:
                                bboxes = np.array(bboxes, dtype=np.float32)

                            self.samples.append((input_path, bboxes))

        self.np_rng.shuffle(self.samples)

    def __len__(self):
        return len(self.samples)

    @property
    def num_classes(self):
        return 1

    @classmethod
    def idx_to_label(cls, idx: int):
        return "dice"

    def apply_augmentation(self, img, bboxes):
        img, bboxes = rotate(img, bboxes, self.rng)
        img, bboxes = flip(img, bboxes, self.rng)
        img = brightness_contrast(img, self.rng)
        img = add_noise(img, self.rng)
        img = blur(img, self.rng)
        return img, bboxes

    def format_output(self, img, bboxes):
        img_w, img_h = self.image_size
        img.set_shape([img_h, img_w, 3 if self.colored else 1])
        bboxes.set_shape([None, 4])
        classes = tf.zeros((tf.shape(bboxes)[0],), dtype=tf.float32)
        classes.set_shape([None])
        return (img, {"boxes": bboxes, "classes": classes})

    def get_tf_dataset(
        self,
        augment: bool = False,
        repeat: int = 1,
        base_only: bool = False,
    ):
        channels = 3 if self.colored else 1
        img_w, img_h = self.image_size

        def load_sample(img_path, bboxes):
            img = tf.io.read_file(img_path)
            img = tf.image.decode_png(img, channels=channels)

            orig_shape = tf.shape(img)
            orig_h = tf.cast(orig_shape[0], tf.float32)
            orig_w = tf.cast(orig_shape[1], tf.float32)

            img = tf.image.resize(img, [img_h, img_w])
            img = tf.cast(img, tf.float32) / 255.0

            bboxes = bboxes.to_tensor()

            scale_x = tf.cast(img_w, tf.float32) / orig_w
            scale_y = tf.cast(img_h, tf.float32) / orig_h
            scales = tf.stack([scale_x, scale_y, scale_x, scale_y])
            bboxes = bboxes * scales

            return img, bboxes

        img_paths = [s[0] for s in self.samples]
        bboxes_list = [s[1] for s in self.samples]

        path_ds = tf.data.Dataset.from_tensor_slices(tf.constant(img_paths, dtype=tf.string))
        bboxes_ds = tf.data.Dataset.from_tensor_slices(tf.ragged.constant(bboxes_list, dtype=tf.float32))
        dataset = tf.data.Dataset.zip((path_ds, bboxes_ds))
        dataset = dataset.map(load_sample, num_parallel_calls=tf.data.AUTOTUNE)

        if base_only:
            return dataset

        dataset = dataset.repeat(repeat)
        if augment:
            dataset = dataset.map(self.apply_augmentation, num_parallel_calls=tf.data.AUTOTUNE)

        dataset = dataset.map(
            lambda img, bboxes, *_: self.format_output(img, bboxes), 
            num_parallel_calls=tf.data.AUTOTUNE
        )

        dataset = dataset.prefetch(tf.data.AUTOTUNE)
        return dataset
