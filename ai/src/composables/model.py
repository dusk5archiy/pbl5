from pydantic import BaseModel
from typing import Any
import yaml
import keras

class ModelInfo(BaseModel):
    module: str
    class_name: str
    config: dict[str, Any] = {}


def load_model(
    task: str,
    model_name: str,
    task_args: BaseModel,
):
    with open(f"config/models/{task}.yml", encoding="utf-8") as f:
        c = yaml.safe_load(f)[model_name]
    c = ModelInfo(**c)
    config = {**task_args.model_dump(), **c.config}
    model = keras.saving.deserialize_keras_object(
        {
            "module": c.module,
            "class_name": c.class_name,
            "config": config,
        }
    )
    return model
