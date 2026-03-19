from src.task.dice_detection.inference import DiceDetectionInference
from src.task.dice_score.inference import DiceScoreInference
from src.utils.time import MeasureTime


class Detector:
    def __init__(
        self,
        dice_detection_model_path: str,
        dice_score_model_path: str,
        dice_detection_image_resolution: tuple[int, int],
        dice_score_image_resolution: tuple[int, int],
        colored: bool,
    ):
        self.dice_detection_model = DiceDetectionInference(
            model_path=dice_detection_model_path,
            image_resolution=dice_detection_image_resolution,
            colored=colored,
        )
        self.dice_score_model = DiceScoreInference(
            model_path=dice_score_model_path,
            image_resolution=dice_score_image_resolution,
            colored=colored,
        )

        self.dice_detection_image_resolution = dice_detection_image_resolution
        self.dice_score_image_resolution = dice_score_image_resolution

    def __call__(self, img):
        original_size = img.size  # (width, height)
        img_resized = img.resize(self.dice_detection_image_resolution)
        with MeasureTime(message="Total time spent"):
            with MeasureTime(message="Detection time"):
                bboxes = self.dice_detection_model.predict(img=img_resized)
            scores = []
            for bbox in bboxes:
                x, y, w, h = bbox
                cropped = img_resized.crop((x, y, x + w, y + h))
                with MeasureTime(message="Score time"):
                    score = self.dice_score_model.predict(img=cropped)
                scores.append(score)

        # Scale bboxes back to original size
        sx, sy = self.dice_detection_image_resolution
        scale_x = original_size[0] / sx
        scale_y = original_size[1] / sy
        scaled_bboxes = []
        for bbox in bboxes:
            x, y, w, h = bbox
            scaled_bboxes.append(
                [int(x * scale_x), int(y * scale_y), int(w * scale_x), int(h * scale_y)]
            )

        return scaled_bboxes, scores
