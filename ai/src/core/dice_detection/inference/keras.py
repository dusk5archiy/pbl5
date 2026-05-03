from .composables import process_predictions

from src.model.dice_detection.yolov8 import YoloV8
from src.model.shared.args import DiceDetectionTaskArgs
import tensorflow as tf

class DotKerasInference:
    def __init__(self, model_path: str, args: DiceDetectionTaskArgs):
        self.args = args
        self.model = tf.keras.models.load_model(
            model_path,
            custom_objects={"YoloV8": YoloV8},
        )

    @tf.function(reduce_retracing=True)
    def _inference(self, x):
        if len(x.shape) == 3:
            x = tf.expand_dims(x, axis=0)

        preds = self.model(x, training=False)

        return process_predictions(
            preds,
            self.args.image_resolution,
            self.args.conf_threshold,
            self.args.iou_threshold,
        )

    def __call__(self, x):
        result = self._inference(x)
        return result.numpy()