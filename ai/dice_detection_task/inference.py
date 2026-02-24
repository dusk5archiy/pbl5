import tensorflow as tf
import numpy as np
from PIL import Image
import os
from .model import get_dice_detection_model


class DiceDetectionInference:
    def __init__(self, model_path: str):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        # Create the model and load weights
        self.model = get_dice_detection_model()
        self.model.load_weights(model_path)

    def __call__(self, img, conf_threshold: float = 0.7, iou_threshold: float = 0.4):
        # img is expected to be a PIL Image
        # Resize using PIL to (width, height) = (640, 480)
        img_resized = img.resize((640, 480))
        img_array = np.array(img_resized).astype(np.float32) / 255.0

        img_batch = tf.expand_dims(img_array, axis=0)  # Add batch dimension

        # Perform inference
        predictions = self.model.predict(img_batch, verbose=0)

        # Extract predictions
        pred_boxes = predictions['boxes'][0]  # xyxy format
        confidences = predictions['confidence'][0]

        # Filter by confidence
        valid_mask = confidences > conf_threshold
        valid_boxes = pred_boxes[valid_mask]
        valid_conf = confidences[valid_mask]

        bboxes = []
        if len(valid_boxes) > 0:
            # Apply NMS
            selected_indices = tf.image.non_max_suppression(
                valid_boxes, valid_conf, max_output_size=10, iou_threshold=iou_threshold
            )
            selected_boxes = tf.gather(valid_boxes, selected_indices)

            for box in selected_boxes:
                x, y, x2, y2 = box.numpy()
                w = x2 - x
                h = y2 - y
                bboxes.append([x, y, w, h])

        return bboxes