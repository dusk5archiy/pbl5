import tensorflow as tf
import numpy as np
from .model import get_dice_score_model


class DiceScoreInference:
    def __init__(self, model_path: str):
        self.model = get_dice_score_model()
        self.model.load_weights(model_path)

    def __call__(self, img):
        # Preprocess the image
        # img is expected to be a PIL Image or numpy array
        if isinstance(img, np.ndarray):
            img_array = img.astype(np.float32) / 255.0
        else:
            # Resize using PIL to (32, 32)
            img_resized = img.resize((32, 32))
            img_array = np.array(img_resized).astype(np.float32) / 255.0

        img_batch = tf.expand_dims(img_array, axis=0)  # Add batch dimension

        # Perform inference
        predictions = self.model.predict(img_batch)

        predicted_class = np.argmax(predictions, axis=1)[0]

        # Scores are 1-6
        score = predicted_class + 1

        return int(score)

