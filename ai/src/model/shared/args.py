from pydantic import BaseModel

class BaseTaskArgs(BaseModel):
    colored: bool
    
    @property
    def num_channels(self):
        return 3 if self.colored else 1

class DiceScoreTaskArgs(BaseTaskArgs):
    image_resolution: tuple[int, int]
    num_classes: int = 6

class DiceDetectionTaskArgs(BaseTaskArgs):
    image_resolution: tuple[int, int]
    conf_threshold: float = 0.5
    iou_threshold: float = 0.5