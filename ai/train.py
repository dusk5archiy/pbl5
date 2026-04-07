import argparse
from src.config import load_config

config = load_config("config/config.yml")

def train_detection(model_name: str):
    from src.task.dice_detection.train import train_savedmodel
    task = config.tasks.dice_detection
    train_savedmodel(
        model_name=model_name,
        config=config,
        task=task,
    )

def convert_detection(quantization = "int8"):
    task = config.tasks.dice_detection
    from src.task.dice_detection.convert import convert2_tflite
    convert2_tflite(
        path=task.training_output_path,
        out_tflite_filename=task.tflite_output_path,
        image_resolution=task.image_resolution,
        colored=config.colored,
        quantization=quantization,
        dataset_path=config.dataset_path if quantization == "int8" else None,
        num_workers=config.num_workers
    )

def train_score(model_name: str):
    from src.task.dice_score.train import train_savedmodel
    task = config.tasks.dice_score
    train_savedmodel(
        model_name=model_name,
        config=config,
        task=task,
    )

def convert_score(quantization="int8"):
    task = config.tasks.dice_score
    from src.task.dice_score.convert import convert2_tflite
    convert2_tflite(
        path=task.training_output_path,
        out_tflite_filename=task.tflite_output_path,
        image_resolution=task.image_resolution,
        quantization=quantization,
        dataset_path=config.dataset_path if quantization == "int8" else None,
        colored=config.colored,
        num_workers=config.num_workers
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--score", action="store_true")
    parser.add_argument("--detection", action="store_true")
    parser.add_argument("--train", action="store_true")
    parser.add_argument("--convert", action="store_true")
    parser.add_argument("--model_name", "-m", type=str, help="Model name to use")

    args = parser.parse_args()

    if args.train and args.score:
        train_score(model_name=args.model_name)

    if args.train and args.detection:
        train_detection(model_name=args.model_name)

    if args.convert and args.score:
        convert_score()

    if args.convert and args.detection:
        convert_detection()


if __name__ == "__main__":
    main()
