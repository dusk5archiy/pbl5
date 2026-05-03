from .keras import DotKerasInference
from .tflite import DotTfliteInference

from src.utils.image import to_grayscale

from PIL import Image
import numpy as np

import os

class DiceScoreInference:
    def __init__(self, 
            model_path: str,
            image_resolution: tuple[int, int],
            colored: bool,
            zero_indexed: bool=False,
        ):
        # Determine model type based on file extension
        _, ext = os.path.splitext(model_path)
        ext = ext.lower()
        
        if ext == ".tflite":
            self.model = DotTfliteInference(model_path)
        else:  # .keras, .h5, or other formats
            self.model = DotKerasInference(model_path)
        
        self.image_resolution = image_resolution
        self.colored = colored
        self.offset = 0 if zero_indexed else 1
        
    def predict(self, img: Image.Image):
        img = img.resize(self.image_resolution)
        img_np = np.array(img)
        return self(img_np)

    def __call__(self, img: np.ndarray):
        # Convert to numpy if it's a TensorFlow tensor
        if hasattr(img, 'numpy'):
            img = img.numpy() # type: ignore
        
        if not self.colored:
            img = to_grayscale(img)
            
        # Check if image is already normalized (0-1 range)
        if img.dtype == np.float32 and img.max() <= 1.0:
            img_array = img
        else:
            img_array = img.astype(np.float32) / 255.0

        pred = self.model(img_array)
        return pred + self.offset