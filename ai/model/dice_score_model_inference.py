import torch
from .dice_score_model import DiceScoreModel
from .dice_score_model_train import inter_transform
import os


class DiceScoreModelInference:
    def __init__(self, model_path):
        if not os.path.exists(model_path):
            raise Exception("Model file not found.")

        self.model = DiceScoreModel()
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()

    def __call__(self, img):
        tensor = inter_transform(img).unsqueeze(0)

        with torch.no_grad():
            output = self.model(tensor)
            _, pred = torch.max(output, 1)
            score = pred.item() + 1

        return score
