from src.config import ParsedConfig
from src.dataset import S7DatasetDiceScore, get_dice_crops
from src.dataset.dice_score.tf import make_tf_dataset

from sklearn.model_selection import train_test_split


def load_dataset(
    config: ParsedConfig,
    batch_size: int,
    task: ParsedConfig.Tasks.DiceScore,
    train_workers: int,
    val_workers: int,
):
    # Get all dice crops
    all_dice_crops = get_dice_crops(
        dataset_path=config.dataset_path,
        num_workers=config.num_workers,
    )

    # Split into 70% train and 30% validation
    train_crops, val_crops = train_test_split(
        all_dice_crops, test_size=0.3, random_state=42
    )

    # Create datasets with split crops
    train_dataset_obj = S7DatasetDiceScore(
        image_resolution=task.image_resolution,
        dice_crops=train_crops,
        colored=config.colored,
        num_workers=train_workers,
        use_random=config.use_random,
        dataset_repeat=task.train_dataset_repeat,
        cache_path="output/dice_score_train",
    )

    val_dataset_obj = S7DatasetDiceScore(
        image_resolution=task.image_resolution,
        dice_crops=val_crops,
        colored=config.colored,
        num_workers=val_workers,
        use_random=config.use_random,
        dataset_repeat=task.val_dataset_repeat,
        cache_path="output/dice_score_val",
    )

    # Create train and val datasets using make_tf_dataset
    train_dataset = make_tf_dataset(
        train_dataset_obj,
        batch_size=batch_size,
        image_resolution=task.image_resolution,
        colored=config.colored,
        use_random=config.use_random,
    )

    val_dataset = make_tf_dataset(
        val_dataset_obj,
        batch_size=batch_size,
        image_resolution=task.image_resolution,
        colored=config.colored,
        use_random=config.use_random,
    )

    return train_dataset, val_dataset

