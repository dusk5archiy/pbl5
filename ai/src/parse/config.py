import yaml
from pydantic import BaseModel


class ParsedConfig(BaseModel):
    dataset_path: str
    num_workers: int = 4
    colored: bool = True

    class Tasks(BaseModel):
        class Base(BaseModel):
            training_output_path: str
            tflite_output_path: str
            inference_path: str
            batch_size: int=1
            epochs: int=50

        class DiceDetection(Base):
            image_resolution: tuple[int, int]

        class DiceScore(Base):
            image_resolution: tuple[int, int]

        dice_detection: DiceDetection
        dice_score: DiceScore

    tasks: Tasks

def load_config(file_path: str):
    with open(file_path, encoding="utf-8") as f:
        content = ParsedConfig(**yaml.safe_load(f))
        
    return content