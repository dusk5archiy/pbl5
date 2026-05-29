from src.backend import yaml

from pydantic import TypeAdapter
import tensorflow as tf

from typing import TypedDict, Unpack

class TrainResults(TypedDict):
    model_name: str
    batch_size: int
    lr: float
    n_epochs: int
    image_resolution: tuple[int, int]
    
def report_training_results(
    output_dir: str,
    model: tf.keras.Model,
    **kwargs: Unpack[TrainResults]
):
    kwargs = TypeAdapter(TrainResults).validate_python(kwargs)
    info = {
        **kwargs,
        "n_params": model.count_params(),
    }

    with open(f"{output_dir}/train.yml", 'w') as f:
        yaml.dump(info, f, default_flow_style=False, sort_keys=False)