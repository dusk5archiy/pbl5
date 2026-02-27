import keras_cv as kcv


def get_dice_detection_model(
    num_classes: int = 1,
    bounding_box_format: str = "xyxy",
    model_name: str = "yolo_v8_xs_backbone",
    fpn_depth: int = 1,
):
    backbone = kcv.models.YOLOV8Backbone.from_preset(model_name)
    model = kcv.models.YOLOV8Detector(
        num_classes=num_classes,
        bounding_box_format=bounding_box_format,
        backbone=backbone,
        fpn_depth=fpn_depth,
    )
    return model
