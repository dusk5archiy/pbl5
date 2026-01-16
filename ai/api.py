from model.dice_pos_model_inference import DicePosModelInference
from model.dice_score_model_inference import DiceScoreModelInference
from PIL import Image
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil


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

        return [[int(x.item()) for x in bbox] for bbox in bboxes], scores


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = Detector(
    dice_pos_model_path="output/dice-pos-model.pt",
    dice_score_model_path="output/dice-score-model.pth",
)


@app.post("/detect")
async def detect_image(file: UploadFile = File(...)):
    var_dir = "var"
    os.makedirs(var_dir, exist_ok=True)
    file_path = os.path.join(var_dir, file.filename or "")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    bboxes, scores = detector(file_path)
    return {"bboxes": bboxes, "scores": scores}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
