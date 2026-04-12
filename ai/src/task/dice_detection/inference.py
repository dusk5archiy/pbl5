import tensorflow as tf
import os
from ai_edge_litert.interpreter import Interpreter
from .utils import decode_dfl
from src.utils.image import to_grayscale
from PIL import Image
from src.model.dice_detection.yolov8 import YoloV8
from src.model.shared.args import DiceDetectionTaskArgs
import numpy as np


@tf.function(reduce_retracing=True)
def process_predictions(
    preds,
    image_resolution,
    conf_threshold: float,
    iou_threshold: float,
):
    # Decode and squeeze
    boxes = decode_dfl(preds["boxes"][0], image_resolution)
    confs = tf.squeeze(preds["classes"][0])

    # Filter by confidence
    mask = confs > conf_threshold
    boxes = boxes[mask]
    confs = confs[mask]

    # Apply NMS
    def empty_case():
        return tf.zeros((0, 4), dtype=tf.float32)

    def non_empty_case():
        indices = tf.image.non_max_suppression(
            boxes,
            confs,
            max_output_size=10,
            iou_threshold=iou_threshold,
        )
        return tf.gather(boxes, indices)

    return tf.cond(tf.equal(tf.shape(boxes)[0], 0), empty_case, non_empty_case)


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


class DotTfliteInference:
    def __init__(self, model_path: str, args: DiceDetectionTaskArgs):
        self.args = args
        self.interpreter = Interpreter(model_path=model_path, num_threads=1)
        input_details = self.interpreter.get_input_details()
        self.interpreter.resize_tensor_input(
            input_details[0]["index"],
            [1, args.image_resolution[1], args.image_resolution[0], args.num_channels],
        )
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.interpreter.allocate_tensors()

    def _inference(self, x):
        if len(x.shape) == 3:
            x = tf.expand_dims(x, axis=0)
        self.interpreter.set_tensor(self.input_details[0]["index"], x)
        self.interpreter.invoke()
        boxes, classes = (
            self.interpreter.get_tensor(output["index"])
            for output in self.output_details
        )
        preds = {"boxes": boxes, "classes": classes}
        return process_predictions(
            preds,
            self.args.image_resolution,
            self.args.conf_threshold,
            self.args.iou_threshold,
        )

    def __call__(self, x):
        return self._inference(x).numpy()


class DiceDetectionInference:
    def __init__(
        self,
        model_path: str,
        image_resolution: tuple[int, int],
        colored: bool,
        conf_threshold: float = 0.5,
        iou_threshold: float = 0.7,
    ):
        # Determine model type based on file extension
        _, ext = os.path.splitext(model_path)
        ext = ext.lower()

        args = DiceDetectionTaskArgs(
            colored=colored,
            conf_threshold=conf_threshold,
            iou_threshold=iou_threshold,
            image_resolution=image_resolution,
        )

        if ext == ".tflite":
            self.model = DotTfliteInference(model_path=model_path, args=args)
        else:  # .keras, .h5, or other formats
            self.model = DotKerasInference(model_path=model_path, args=args)

        self.colored = colored
        self.image_resolution = image_resolution
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold

    def predict(self, img: Image.Image):
        img = img.resize(self.image_resolution)
        img_np = np.array(img)
        return self(img_np)

    def __call__(self, img: np.ndarray):
        if not self.colored:
            img = to_grayscale(img)
        # Check if image is already normalized (0-1 range)
        if img.dtype == np.float32 and img.max() <= 1.0:
            img_array = img
        else:
            img_array = img.astype(np.float32) / 255.0

        bboxes = []
        for x, y, x2, y2 in self.model(img_array):
            w = x2 - x
            h = y2 - y
            bboxes.append([x, y, w, h])
        return bboxes
