import os
import tensorflow as tf
from src.config import ParsedConfig
from src.dataset.dice_detection.custom_dice_dataset import CustomDiceDataset


def load_dataset(
    config: ParsedConfig,
    task: ParsedConfig.Tasks.DiceDetection,
    batch_size: int,
):
    dataset_manager = CustomDiceDataset(
        root_dir=config.dataset_path,
        seed=42,
        image_size=task.image_resolution,
        colored=config.colored,
    )
    total_samples = len(dataset_manager.samples)

    train_count = int(total_samples * 0.70)
    val_count = int(total_samples * 0.15)

    img_w, img_h = task.image_resolution
    suffix = f"-{'c' if config.colored else 'g'}-{img_w}-{img_h}"
    cache_dir = os.path.abspath("output/cache")
    os.makedirs(cache_dir, exist_ok=True)

    base_dataset = dataset_manager.get_tf_dataset(base_only=True)

    train_dataset = (
        base_dataset.take(train_count)
        .cache(os.path.join(cache_dir, f"train{suffix}"))
        .repeat(task.train_dataset_repeat)
    )
    train_dataset = train_dataset.map(
        dataset_manager.apply_augmentation, num_parallel_calls=tf.data.AUTOTUNE
    )
    train_dataset = train_dataset.map(
        dataset_manager.format_output,
        num_parallel_calls=tf.data.AUTOTUNE,
    )

    train_dataset = train_dataset.batch(batch_size, drop_remainder=True).prefetch(
        tf.data.AUTOTUNE
    )

    val_dataset = (
        base_dataset.skip(train_count)
        .take(val_count)
        .cache(os.path.join(cache_dir, f"val{suffix}"))
        .repeat(task.val_dataset_repeat)
    )
    val_dataset = val_dataset.map(
        dataset_manager.format_output, num_parallel_calls=tf.data.AUTOTUNE
    )
    val_dataset = val_dataset.batch(batch_size, drop_remainder=True).prefetch(
        tf.data.AUTOTUNE
    )

    return train_dataset, val_dataset
