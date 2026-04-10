import tensorflow as tf
from pydantic import TypeAdapter
from typing import TypedDict, Unpack
from src.backend import yaml

class TrainResults(TypedDict):
    model_name: str
    batch_size: int
    n_epochs: int
    image_resolution: tuple[int, int]
    
def report_training_results(
    path_base: str,
    model: tf.keras.Model,
    **kwargs: Unpack[TrainResults]
) -> None:
    kwargs = TypeAdapter(TrainResults).validate_python(kwargs)
    info = {
        **kwargs,
        "n_params": model.count_params(),
    }

    with open(path_base + ".yml", 'w') as f:
        yaml.dump(info, f, default_flow_style=False, sort_keys=False)