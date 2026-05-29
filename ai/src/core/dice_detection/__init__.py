from src.backend import argparse
from src.config import ParsedConfig

from typing import Callable

class TaskArgParser:
    def __init__(self, config: ParsedConfig):
        self.config = config

    def add_subparsers(self, parser: argparse.ArgumentParser):
        # Add subparsers for modes
        subparsers = parser.add_subparsers(dest="mode", help="Available modes", required=True)

        # Train subparser
        train_parser = subparsers.add_parser("train", help="Train the model")
        train_parser.add_argument("--model_name", "-m", type=str, required=True)
        train_parser.add_argument("--batch_size", type=int, required=True)
        train_parser.add_argument("--lr", type=float, required=False, default=0.001)
        train_parser.add_argument("--epochs", type=int, required=True)
        train_parser.add_argument("--alias", type=str, required=False, default=None, help="Optional alias for the output folder")

        # Eval subparser
        eval_parser = subparsers.add_parser("eval", help="Evaluate the model")
        eval_parser.add_argument("--model_path", "-m", type=str, required=True)

        # Convert subparser
        convert_parser = subparsers.add_parser("convert", help="Convert the model")
        convert_parser.add_argument("--model_path", "-m", type=str, required=True)
        convert_parser.add_argument("--quantization", type=str, default="int8")

    def get_action(self, args: argparse.Namespace) -> Callable[[], None]:
        from .train import train_savedmodel
        from .evaluate import evaluate_model
        from .convert import convert2_tflite

        task = self.config.tasks.dice_detection

        # Return action based on mode
        match args.mode:
            case "train":
                return lambda: train_savedmodel(
                    model_name=args.model_name,
                    config=self.config,
                    batch_size=args.batch_size,
                    lr=args.lr,
                    epochs=args.epochs,
                    alias=args.alias,
                    task=task,
                )
            case "eval":
                return lambda: evaluate_model(
                    model_path=args.model_path,
                    config=self.config,
                    task=task,
                )
            case "convert":
                return lambda: convert2_tflite(
                    path=args.model_path,
                    image_resolution=task.image_resolution,
                    quantization=args.quantization,
                    dataset_path=self.config.dataset_path if args.quantization == "int8" else None,
                    colored=self.config.colored,
                )

        return lambda: None