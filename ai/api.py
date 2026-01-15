from model.dice_pos_model_inference import DicePosModelInference
from model.dice_score_model_inference import DiceScoreModelInference
from PIL import Image


class Detector:
    def __init__(self, dice_pos_model_path: str, dice_score_model_path: str):
        self.dice_pos_model = DicePosModelInference(model_path=dice_pos_model_path)
        self.dice_score_model = DiceScoreModelInference(
            model_path=dice_score_model_path
        )

    def __call__(self, image_path):
        bboxes = self.dice_pos_model(image_path=image_path)
        img = Image.open(image_path).convert("RGB")
        scores = []
        for bbox in bboxes:
            x, y, w, h = bbox
            cropped = img.crop((x, y, x + w, y + h)).resize((32, 32))
            score = self.dice_score_model(img=cropped)
            scores.append(score)

        return bboxes, scores


if __name__ == "__main__":
    dice_pos_model_path = "output/dice-pos-model.pt"
    dice_score_model_path = "output/dice-score-model.pth"
    detector = Detector(
        dice_pos_model_path=dice_pos_model_path,
        dice_score_model_path=dice_score_model_path,
    )
