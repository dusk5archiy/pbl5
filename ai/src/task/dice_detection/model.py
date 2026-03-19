from src.model.yolo_v8.yolo_v8_detector import YOLOV8Detector
import tensorflow as tf

def _load_backbone(colored: bool=True):
    c = {
        "name": "yolov8_backbone",
        "trainable": True,
        "include_rescaling": True,
        "input_shape": (None, None, 3 if colored else 1),
        "stackwise_channels": [8, 16, 32, 64],
        "stackwise_depth": [1, 2, 2, 1],
        "activation": "swish"
    }
    
    backbone_config = {
        "module": "src.model.yolo_v8.yolo_v8_backbone",
        "class_name": "YOLOV8Backbone",
        "config": c,
        "weights": None
    }

    model = tf.keras.saving.deserialize_keras_object(backbone_config)
    return model
    


def load_model(
    bounding_box_format: str='xywh',
    fpn_depth: int=1,
    colored: bool=True
) -> YOLOV8Detector:
    backbone = _load_backbone(colored=colored)

    model = YOLOV8Detector(
        num_classes=1,
        backbone=backbone,
        bounding_box_format=bounding_box_format,
        fpn_depth=fpn_depth,
    )
    return model