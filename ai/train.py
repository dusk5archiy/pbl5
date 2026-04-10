import argparse
from argparse import Namespace
from src.config import load_config

config = load_config("config/config.yml")

def train_detection(args: Namespace):
    from src.task.dice_detection.train import train_savedmodel
    task = config.tasks.dice_detection
    train_savedmodel(
        model_name=args.model_name,
        config=config,
        task=task,
    )

def convert_detection(args: Namespace):
    task = config.tasks.dice_detection
    from src.task.dice_detection.convert import convert2_tflite
    convert2_tflite(
        path=args.model_name,
        image_resolution=task.image_resolution,
        colored=config.colored,
        quantization=args.quantization,
        dataset_path=config.dataset_path if args.quantization == "int8" else None,
        num_workers=config.num_workers
    )

def train_score(args: Namespace):
    from src.task.dice_score.train import train_savedmodel
    task = config.tasks.dice_score
    train_savedmodel(
        model_name=args.model_name,
        config=config,
        task=task,
    )

def convert_score(args: Namespace):
    task = config.tasks.dice_score
    from src.task.dice_score.convert import convert2_tflite
    convert2_tflite(
        path=args.model_name,
        image_resolution=task.image_resolution,
        quantization=args.quantization,
        dataset_path=config.dataset_path if args.quantization == "int8" else None,
        colored=config.colored,
        num_workers=config.num_workers
    )

def evaluate_detection(args: Namespace):
    from src.task.dice_detection.evaluate import evaluate_model
    task = config.tasks.dice_detection
    evaluate_model(
        model_path=args.model_name,
        config=config,
        task=task,
    )

def evaluate_score(args: Namespace):
    from src.task.dice_score.evaluate import evaluate_model
    task = config.tasks.dice_score
    evaluate_model(
        model_path=args.model_name,
        config=config,
        task=task,
    )

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--score", action="store_true")
    parser.add_argument("--detection", action="store_true")
    parser.add_argument("--train", "-t", action="store_true")
    parser.add_argument("--convert", "-c", action="store_true")
    parser.add_argument("--eval", "-e", action="store_true")
    parser.add_argument("--model_name", "-m", type=str, help="Model name to use")
    parser.add_argument("--quantization", type=str, default="int8", help="Quantization type for TFLite conversion (int8, float16, float32)")

    args = parser.parse_args()

    if args.train and args.score:
        train_score(args)

    if args.train and args.detection:
        train_detection(args)

    if args.convert and args.score:
        convert_score(args)

    if args.convert and args.detection:
        convert_detection(args)

    if args.eval and args.score:
        evaluate_score(args)

    if args.eval and args.detection:
        evaluate_detection(args)


if __name__ == "__main__":
    main()
