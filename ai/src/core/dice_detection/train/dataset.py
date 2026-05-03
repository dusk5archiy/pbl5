from src.config import ParsedConfig
from src.dataset import (
    get_image_detection_datas,
    S7DatasetDiceDetection,
)
from src.dataset.dice_detection.tf import make_tf_dataset

from sklearn.model_selection import train_test_split

def load_dataset(
    config: ParsedConfig,
    task: ParsedConfig.Tasks.DiceDetection,
    batch_size: int,
    train_workers: int,
    val_workers: int,
):
    all_image_datas = get_image_detection_datas(
        dataset_path=config.dataset_path, num_workers=config.num_workers
    )
    # Split into 70% train and 30% validation
    train_datas, val_datas = train_test_split(
        all_image_datas, test_size=0.3, random_state=42
    )
    train_dataset_obj = S7DatasetDiceDetection(
        image_resolution=task.image_resolution,
        image_datas=train_datas,
        colored=config.colored,
        use_random=config.use_random,
        cache_path="output/dice_detection_train",
        dataset_repeat=task.train_dataset_repeat,
        num_workers=train_workers,
    )

    val_dataset_obj = S7DatasetDiceDetection(
        image_resolution=task.image_resolution,
        image_datas=val_datas,
        colored=config.colored,
        use_random=config.use_random,
        cache_path="output/dice_detection_val",
        dataset_repeat=task.val_dataset_repeat,
        num_workers=val_workers,
    )

    train_dataset = make_tf_dataset(
        train_dataset_obj,
        batch_size=batch_size,
        image_resolution=task.image_resolution,
        colored=config.colored,
        use_random=config.use_random
    )

    val_dataset = make_tf_dataset(
        val_dataset_obj,
        batch_size=batch_size,
        image_resolution=task.image_resolution,
        colored=config.colored,
        use_random=config.use_random
    )
    
    return train_dataset, val_dataset

