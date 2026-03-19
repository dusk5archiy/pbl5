import tensorflow as tf
import numpy as np
from ai_edge_litert.interpreter import Interpreter
from .utils import decode_dfl
from src.utils.image import to_grayscale
from PIL import Image


class DiceDetectionInference:
    def __init__(
        self,
        model_path: str,
        image_resolution: tuple[int, int],
        colored: bool,
        conf_threshold: float = 0.5,
        iou_threshold: float = 0.7,
    ):
        num_channels = 3 if colored else 1
        self.interpreter = Interpreter(model_path=model_path)
        input_details = self.interpreter.get_input_details()
        self.interpreter.resize_tensor_input(
            input_details[0]["index"],
            [1, image_resolution[1], image_resolution[0], num_channels],
        )
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.interpreter.allocate_tensors()

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
        img_array = img.astype(np.float32) / 255.0
        img_tensor = tf.expand_dims(img_array, axis=0)  # Add batch dimension

        # Perform inference
        self.interpreter.set_tensor(self.input_details[0]["index"], img_tensor)
        self.interpreter.invoke()
        pred = {
            output["name"]: self.interpreter.get_tensor(output["index"])
            for output in self.output_details
        }
        dfl_logits = pred["Identity"][0]  # (_, 64)
        confidences = pred["Identity_1"][0].squeeze()
        pred_boxes = decode_dfl(
            dfl_logits, self.image_resolution
        )  # (_, 4) - decoded coordinates

        # Filter by confidence
        valid_mask = confidences > self.conf_threshold
        valid_boxes = pred_boxes[valid_mask]
        valid_conf = confidences[valid_mask]

        bboxes = []
        if len(valid_boxes) > 0:
            # Apply NMS
            selected_indices = tf.image.non_max_suppression(
                valid_boxes,
                valid_conf,
                max_output_size=10,
                iou_threshold=self.iou_threshold,
            )
            selected_boxes = tf.gather(valid_boxes, selected_indices)

            for box in selected_boxes:
                x, y, x2, y2 = box.numpy()
                w = x2 - x
                h = y2 - y
                bboxes.append([x, y, w, h])
        return bboxes

