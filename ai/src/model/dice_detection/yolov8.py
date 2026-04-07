import tensorflow as tf
from src.external.yolo_v8.yolo_v8_detector import YOLOV8Detector
from src.model.shared.args import DiceDetectionTaskArgs
from src.model.shared.base import BaseAIModel

class YoloV8(BaseAIModel, YOLOV8Detector):
    class Config(DiceDetectionTaskArgs):
        stackwise_channels: list[int]
        stackwise_depth: list[int]
        activation: str="swish"
        bbox_format: str='xywh'

    def __init__(self, config: Config):
        fpn_depth=1
        c = {
            "name": "yolov8_backbone",
            "trainable": True,
            "include_rescaling": True,
            "input_shape": (None, None, config.num_channels),
            "stackwise_channels": config.stackwise_channels,
            "stackwise_depth": config.stackwise_depth,
            "activation": config.activation
        }
        
        backbone_config = {
            "module": "src.external.yolo_v8.yolo_v8_backbone",
            "class_name": "YOLOV8Backbone",
            "config": c,
            "weights": None
        }

        backbone = tf.keras.saving.deserialize_keras_object(backbone_config)
        YOLOV8Detector.__init__(
            self,
            num_classes=1,
            backbone=backbone,
            bounding_box_format=config.bbox_format,
            fpn_depth=fpn_depth,
        )

    @classmethod
    def from_config(cls, config):
        result =  cls(config=cls.Config(**config))
        return result