import os
import tensorflow as tf
from src.config import ParsedConfig
from src.dataset.dice_detection.custom_dice_dataset import CustomDiceDataset

def load_dataset(config: ParsedConfig, task: ParsedConfig.Tasks.DiceDetection, batch_size: int = 1):
    # 1. Initialize the same optimized manager
    dataset_manager = CustomDiceDataset(
        root_dir=config.dataset_path,
        seed=42,
        image_size=task.image_resolution,
        colored=config.colored,
    )
    total_samples = len(dataset_manager.samples)
    
    train_count = int(total_samples * 0.70)
    val_count = int(total_samples * 0.15)
    test_count = total_samples - train_count - val_count

    img_w, img_h = task.image_resolution
    suffix = f"-{'c' if config.colored else 'g'}-{img_w}-{img_h}"
    cache_dir = os.path.abspath("output/cache/dice_detection")
    os.makedirs(cache_dir, exist_ok=True)

    # 2. Get the base dataset
    base_dataset = dataset_manager.get_tf_dataset(base_only=True)

    # 3. Take the last 15% (Test set)
    # Skip train (70%) and val (15%) to get the remaining 15%
    test_dataset = (
        base_dataset.skip(train_count + val_count)
        .take(test_count)
        .cache(os.path.join(cache_dir, f"test{suffix}"))
    )

    # 4. Format for evaluation
    test_dataset = test_dataset.map(
        lambda img, bboxes, *_: dataset_manager.format_output(img, bboxes),
        num_parallel_calls=tf.data.AUTOTUNE
    )
    test_dataset = test_dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)

    return dataset_manager, test_dataset




