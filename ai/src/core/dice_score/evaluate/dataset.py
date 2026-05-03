from src.config import ParsedConfig
from src.dataset import S7DatasetDiceScore, get_dice_crops
from src.dataset.dice_score.tf import make_tf_dataset
from src.utils.determ import enable_determ

from sklearn.model_selection import train_test_split

def load_dataset(config: ParsedConfig, task: ParsedConfig.Tasks.DiceScore):
    # Prepare validation dataset
    all_dice_crops = get_dice_crops(
        dataset_path=config.dataset_path,
        num_workers=config.num_workers,
    )

    # Split into train and validation (using same split as training)
    enable_determ()
    _, val_crops = train_test_split(all_dice_crops, test_size=0.3, random_state=42)

    val_dataset_obj = S7DatasetDiceScore(
        image_resolution=task.image_resolution,
        dice_crops=val_crops,
        colored=config.colored,
        num_workers=4,
        use_random=False,
        dataset_repeat=task.val_dataset_repeat,
        cache_path="output/dice_score_eval",
    )

    val_dataset = make_tf_dataset(
        val_dataset_obj,
        batch_size=1,
        image_resolution=task.image_resolution,
        colored=config.colored,
        use_random=config.use_random,
    )

    return val_dataset_obj, val_dataset


