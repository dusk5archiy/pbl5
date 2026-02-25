import tensorflow as tf
import numpy as np
from ai_edge_litert.interpreter import Interpreter


class DiceScoreInference:
    def __init__(self, model_path: str):
        self.interpreter = Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def __call__(self, img):
        # Preprocess the image
        # img is expected to be a PIL Image or numpy array
        if isinstance(img, np.ndarray):
            img_array = img.astype(np.float32) / 255.0
        else:
            # Resize using PIL to (32, 32)
            img_resized = img.resize((32, 32))
            img_array = np.array(img_resized).astype(np.float32) / 255.0

        img_tensor = tf.expand_dims(img_array, axis=0)  # Add batch dimension

        # Perform inference
        self.interpreter.set_tensor(self.input_details[0]["index"], img_tensor.numpy())
        self.interpreter.invoke()
        pred = self.interpreter.get_tensor(self.output_details[0]["index"])
        pred = pred[0]

        predicted_class = np.argmax(pred)

        # Scores are 1-6
        score = predicted_class + 1

        return int(score)
