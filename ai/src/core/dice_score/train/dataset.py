import os
import tensorflow as tf
from src.config import ParsedConfig
from src.dataset.dice_score.custom_dice_dataset import CustomDiceScoreDataset

def load_dataset(
    config: ParsedConfig,
    task: ParsedConfig.Tasks.DiceScore,
    batch_size: int,
):
    # 1. Initialize a single manager
    dataset_manager = CustomDiceScoreDataset(
        root_dir=config.dataset_path, 
        image_size=task.image_resolution,
        colored=config.colored,
        seed=42
    )
    total_samples = len(dataset_manager.samples)
    
    train_count = int(total_samples * 0.70)
    val_count = int(total_samples * 0.15)

    img_w, img_h = task.image_resolution
    suffix = f"-{'c' if config.colored else 'g'}-{img_w}-{img_h}"
    cache_dir = os.path.abspath("output/cache/dice_score")
    os.makedirs(cache_dir, exist_ok=True)

    # 2. Get the base dataset once (loading and resizing)
    base_dataset = dataset_manager.get_tf_dataset(
        base_only=True
    )

    # 3. Split the TF dataset using take and skip
    train_ds = base_dataset.take(train_count).cache(os.path.join(cache_dir, f"train{suffix}"))
    val_ds = base_dataset.skip(train_count).take(val_count).cache(os.path.join(cache_dir, f"val{suffix}"))

    # 4. Apply training-specific steps (repeat, augment, format)
    train_dataset = train_ds.repeat(task.train_dataset_repeat)
    train_dataset = train_dataset.map(dataset_manager.apply_augmentation, num_parallel_calls=tf.data.AUTOTUNE)
    train_dataset = train_dataset.map(dataset_manager.format_output, num_parallel_calls=tf.data.AUTOTUNE)
    train_dataset = train_dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)

    # 5. Apply validation-specific steps (format)
    val_dataset = val_ds.map(dataset_manager.format_output, num_parallel_calls=tf.data.AUTOTUNE)
    val_dataset = val_dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)
    
    return train_dataset, val_dataset


