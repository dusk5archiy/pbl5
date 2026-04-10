import tensorflow as tf
import numpy as np
from ai_edge_litert.interpreter import Interpreter
from PIL import Image
from src.utils.image import to_grayscale


class DiceScoreInference:
    def __init__(self, 
            model_path: str,
            image_resolution: tuple[int, int],
            colored: bool
        ):
        self.interpreter = Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        self.image_resolution = image_resolution
        self.colored = colored
        
    def predict(self, img: Image.Image):
        img = img.resize(self.image_resolution)
        img_np = np.array(img)
        return self(img_np)

    def __call__(self, img: np.ndarray):
        # Convert to numpy if it's a TensorFlow tensor
        if hasattr(img, 'numpy'):
            img = img.numpy() # type: ignore
            
        if not self.colored:
            img_array = img
            
        # Check if image is already normalized (0-1 range)
        if img.dtype == np.float32 and img.max() <= 1.0:
            img_array = img
        else:
            img_array = img.astype(np.float32) / 255.0
            
        img_tensor = tf.expand_dims(img_array, axis=0)  # Add batch dimension

        # Perform inference
        self.interpreter.set_tensor(self.input_details[0]["index"], img_tensor)
        self.interpreter.invoke()
        pred = self.interpreter.get_tensor(self.output_details[0]["index"])
        pred = pred[0]

        predicted_class = np.argmax(pred)

        return int(predicted_class) + 1