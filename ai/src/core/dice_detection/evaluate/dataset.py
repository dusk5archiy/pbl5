from src.config import ParsedConfig
from src.dataset import get_image_detection_datas, S7DatasetDiceDetection
from src.dataset.dice_detection.tf import make_tf_dataset

from sklearn.model_selection import train_test_split

def load_dataset(config, task: ParsedConfig.Tasks.DiceDetection):
    # Prepare validation dataset
    all_image_datas = get_image_detection_datas(
        dataset_path=config.dataset_path, num_workers=config.num_workers
    )

    # Split into train and validation (using same split as training)
    _, val_datas = train_test_split(all_image_datas, test_size=0.3, random_state=42)

    val_dataset_obj = S7DatasetDiceDetection(
        image_resolution=task.image_resolution,
        image_datas=val_datas,
        colored=config.colored,
        use_random=False,
        cache_path="output/dice_detection_val",
        dataset_repeat=task.val_dataset_repeat,
        num_workers=4,
    )

    val_dataset = make_tf_dataset(
        val_dataset_obj,
        batch_size=1,
        image_resolution=task.image_resolution,
        colored=config.colored,
        use_random=config.use_random
    )

    return val_dataset_obj, val_dataset


