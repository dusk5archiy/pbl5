from .keras import DotKerasInference
from .tflite import DotTfliteInference

from src.functions.bbox import xyxy_to_xywh
from src.model.shared.args import DiceDetectionTaskArgs
from src.utils.image import to_grayscale

from PIL import Image
import numpy as np

import os


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

        pred = self.model(img_array)

        return xyxy_to_xywh(pred)

