from pydantic import BaseModel
import yaml


class ParsedConfig(BaseModel):
    dataset_path: str
    num_workers: int
    colored: bool
    use_random: bool

    class Tasks(BaseModel):
        class Base(BaseModel):
            name: str
            inference_path: str
            train_dataset_repeat: int
            val_dataset_repeat: int

        class DiceDetection(Base):
            name: str="dice_detection"
            image_resolution: tuple[int, int]

        class DiceScore(Base):
            name: str="dice_score"
            image_resolution: tuple[int, int]

        class FrameDetection(BaseModel):
            similarity_threshold: float
            qualified_consecutive_frames: int

        dice_detection: DiceDetection
        dice_score: DiceScore
        frame_detection: FrameDetection

    tasks: Tasks


def load_config(file_path: str):
    with open(file_path, encoding="utf-8") as f:
        content = ParsedConfig(**yaml.safe_load(f))

    return content
