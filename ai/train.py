from src.config import load_config
from src.core.dice_detection import TaskArgParser as DetectionArgParser
from src.core.dice_score import TaskArgParser as ScoreArgParser

import argparse

config = load_config("config/config.yml")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="task", help="Available tasks", required=True)

    # Score task subparser
    score_parser = subparsers.add_parser("score", help="Dice score task")
    score_arg_parser = ScoreArgParser(config=config)
    score_arg_parser.add_subparsers(score_parser)

    # Detection task subparser
    detection_parser = subparsers.add_parser("detection", help="Dice detection task")
    detection_arg_parser = DetectionArgParser(config=config)
    detection_arg_parser.add_subparsers(detection_parser)

    # Parse all arguments
    args = parser.parse_args()

    # Get action based on task
    action = lambda: None
    match args.task:
        case "score":
            action = score_arg_parser.get_action(args)
        case "detection":
            action = detection_arg_parser.get_action(args)
    
    action()
