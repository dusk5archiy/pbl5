import yaml
from pydantic import BaseModel

class ConfigModel(BaseModel):
    dataset_path: str
    num_workers: int = 8

def load_config(file_path: str):
    with open(file_path, encoding="utf-8") as f:
        content = ConfigModel(**yaml.safe_load(f))
        
    return content