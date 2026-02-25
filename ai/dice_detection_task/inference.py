import tensorflow as tf
import numpy as np
from ai_edge_litert.interpreter import Interpreter
from dice_detection_task.utils import decode_dfl


class DiceDetectionInference:
    def __init__(self, model_path: str, use_litert: bool = False):
        # Load the flex delegate
        self.use_litert = use_litert
        if self.use_litert:
            self.interpreter = Interpreter(model_path=model_path)
            input_details = self.interpreter.get_input_details()
            self.interpreter.resize_tensor_input(
                input_details[0]["index"], [1, 480, 640, 3]
            )
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            self.interpreter.allocate_tensors()

        else:
            self.model = tf.saved_model.load(model_path)

    def __call__(self, img, conf_threshold: float = 0.1, iou_threshold: float = 0.7):
        # img is expected to be a PIL Image
        # Resize using PIL to (width, height) = (640, 480)
        img_resized = img.resize((640, 480))
        img_array = np.array(img_resized).astype(np.float32) / 255.0

        img_tensor = tf.expand_dims(img_array, axis=0)  # Add batch dimension

        # Perform inference
        if self.use_litert:
            self.interpreter.set_tensor(
                self.input_details[0]["index"], img_tensor.numpy()
            )
            self.interpreter.invoke()
            pred = {
                output["name"]: self.interpreter.get_tensor(output["index"])
                for output in self.output_details
            }
            dfl_logits = pred["StatefulPartitionedCall:0"][0]  # (_, 64)
            pred_boxes = decode_dfl(dfl_logits)  # (_, 4) - decoded coordinates
            confidences = pred["StatefulPartitionedCall:1"][0].squeeze()

        else:
            pred = self.model(img_tensor)
            dfl_logits = pred["boxes"][0]  # (_, 64)
            pred_boxes = decode_dfl(dfl_logits)  # (_, 4) - decoded coordinates
            confidences = tf.squeeze(pred["classes"][0])

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
