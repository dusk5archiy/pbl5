import tensorflow as tf
import numpy as np


class DiceDetectionInference:
    def __init__(self, model_path: str):
        self.model = tf.keras.models.load_model(model_path)

    def __call__(self, img, conf_threshold: float = 0.1, iou_threshold: float = 0.9):
        # img is expected to be a PIL Image
        # Resize using PIL to (width, height) = (640, 480)
        img_resized = img.resize((640, 480))
        img_array = np.array(img_resized).astype(np.float32) / 255.0

        img_batch = tf.expand_dims(img_array, axis=0)  # Add batch dimension

        # Perform inference
        predictions = self.model.predict(img_batch)

        # Extract predictions
        pred_boxes = predictions["boxes"][0]  # xyxy format
        confidences = predictions["confidence"][0]

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
                x, y, w, h = box.numpy()
                bboxes.append([x, y, w, h])

        return bboxes

