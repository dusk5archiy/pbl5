import argparse
from src.parse.config import load_config

config = load_config("config/config.yml")

def train_detection():
    task = config.tasks.dice_detection

    from src.task.dice_detection.train import train_savedmodel
    train_savedmodel(
        dataset_path=config.dataset_path,
        image_resolution=task.image_resolution,
        batch_size=task.batch_size,
        path=task.training_output_path,
        epochs=task.epochs,
        num_workers=config.num_workers,
        colored=config.colored
    )

    from src.task.dice_detection.convert import convert2_tflite
    convert2_tflite(
        path=task.training_output_path,
        out_tflite_filename=task.tflite_output_path,
        image_resolution=task.image_resolution,
        colored=config.colored
    )

def train_score():
    task = config.tasks.dice_score
    from src.task.dice_score.train import train_savedmodel
    train_savedmodel(
        dataset_path=config.dataset_path,
        image_resolution=task.image_resolution,
        batch_size=task.batch_size,
        path=task.training_output_path,
        epochs=task.epochs,
        num_workers=config.num_workers,
        colored=config.colored
    )

    from src.task.dice_score.convert import convert2_tflite
    convert2_tflite(
        path=task.training_output_path,
        out_tflite_filename=task.tflite_output_path,
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--score", action="store_true")
    parser.add_argument("--detection", action="store_true")

    args = parser.parse_args()

    if args.score:
        train_score()

    if args.detection:
        train_detection()


if __name__ == "__main__":
    main()
