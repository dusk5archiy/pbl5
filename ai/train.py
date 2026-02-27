import argparse
from ults.config import load_config


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--score", action="store_true")
    parser.add_argument("--detection", action="store_true")

    args = parser.parse_args()

    if args.score:
        from training.dice_score.train import train_savedmodel
        from training.dice_score.conv import conv2_tflite
        config = load_config(file_path="config/train.yml")
        train_savedmodel(
            dataset_path=config.dataset_path,
            output_savedmodel_dir="output/dice_score",
            num_workers=config.num_workers,
        )
        conv2_tflite(
            inp_savedmodel_dir="output/dice_score",
            out_tflite_filename="output/dice_score_model.tflite",
        )

    elif args.detection:
        from training.dice_detection.train import train_savedmodel
        from training.dice_detection.conv import conv2_tflite
        config = load_config(file_path="config/train.yml")
        train_savedmodel(
            dataset_path=config.dataset_path,
            output_savedmodel_dir="output/dice_detection",
            num_workers=config.num_workers,
        )
        conv2_tflite(
            inp_savedmodel_dir="output/dice_detection",
            out_tflite_filename="output/dice_detection_model.tflite",
        )


if __name__ == "__main__":
    main()
