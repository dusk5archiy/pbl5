import os
from ultralytics.models import YOLO


class DicePosModelInference:
    def __init__(self, model_path: str):
        if not os.path.exists(model_path):
            raise Exception("Model file not found.")

        self.model = YOLO(model_path)

    def __call__(self, image_path: str):
        results = self.model(image_path, imgsz=256, conf=0.25, verbose=False)
        bboxes = []
        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            for box in boxes:
                x1, y1, x2, y2 = box

                x = x1
                y = y1
                w = x2 - x1
                h = y2 - y1

                bboxes.append([x, y, w, h])

        return bboxes
