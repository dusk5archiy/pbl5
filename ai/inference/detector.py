from inference.dice_detection.inference import DiceDetectionInference
from inference.dice_score.inference import DiceScoreInference
from ults.time import MeasureTime

class Detector:
    def __init__(self, dice_detection_model_path: str, dice_score_model_path: str):
        self.dice_detection_model = DiceDetectionInference(
            model_path=dice_detection_model_path
        )
        self.dice_score_model = DiceScoreInference(model_path=dice_score_model_path)

    def __call__(self, img):
        original_size = img.size  # (width, height)
        img_resized = img.resize((640, 480))
        with MeasureTime(message="Total time spent"):
            with MeasureTime(message="Detection time"):
                bboxes = self.dice_detection_model(img=img_resized)
            scores = []
            for bbox in bboxes:
                x, y, w, h = bbox
                cropped = img_resized.crop((x, y, x + w, y + h)).resize((32, 32))
                with MeasureTime(message="Score time"):
                    score = self.dice_score_model(img=cropped)
                scores.append(score)

        # Scale bboxes back to original size
        scale_x = original_size[0] / 640
        scale_y = original_size[1] / 480
        scaled_bboxes = []
        for bbox in bboxes:
            x, y, w, h = bbox
            scaled_bboxes.append([int(x * scale_x), int(y * scale_y), int(w * scale_x), int(h * scale_y)])

        return scaled_bboxes, scores