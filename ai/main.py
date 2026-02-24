from dice_detection_task.inference import DiceDetectionInference
from dice_score_task.inference import DiceScoreInference
from PIL import Image
from fastapi import FastAPI, File, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import io
import yaml
import os


# Load config
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

front_port = config['front']['port']


class Detector:
    def __init__(self, dice_detection_model_path: str, dice_score_model_path: str):
        self.dice_detection_model = DiceDetectionInference(model_path=dice_detection_model_path)
        self.dice_score_model = DiceScoreInference(model_path=dice_score_model_path)

    def __call__(self, img):
        bboxes = self.dice_detection_model(img=img)
        scores = []
        for bbox in bboxes:
            x, y, w, h = bbox
            cropped = img.crop((x, y, x + w, y + h)).resize((32, 32))
            score = self.dice_score_model(img=cropped)
            scores.append(score)

        return [[int(x) for x in bbox] for bbox in bboxes], scores


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for WebSocket
    allow_credentials=False,  # No credentials needed for dice detection
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = Detector(
    dice_detection_model_path="models/best_detection_model.keras",
    dice_score_model_path="models/best_model.keras",
)


@app.websocket("/detect")
async def detect_image_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            image = Image.open(io.BytesIO(data)).convert("RGB")
            bboxes, scores = detector(image)
            await websocket.send_json({"bboxes": bboxes, "scores": scores})
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)