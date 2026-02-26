from dice_detection_task.inference import DiceDetectionInference
from dice_score_task.inference import DiceScoreInference
from PIL import Image
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import io
import yaml
import os
import time
import traceback
from keras import backend
from ults.time import MeasureTime


# Load config
config_path = os.path.join(os.path.dirname(__file__), "..", "config.yml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

front_port = config["front"]["port"]


class Detector:
    def __init__(self, dice_detection_model_path: str, dice_score_model_path: str):
        start = time.time()
        backend.clear_session()

        self.dice_detection_model = DiceDetectionInference(
            model_path=dice_detection_model_path
        )
        self.dice_score_model = DiceScoreInference(model_path=dice_score_model_path)
        end = time.time()
        print(f"Time to initiate: {end - start:.4f}")

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
            scaled_bboxes.append([x * scale_x, y * scale_y, w * scale_x, h * scale_y])

        return [[int(x) for x in bbox] for bbox in scaled_bboxes], scores


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for WebSocket
    allow_credentials=False,  # No credentials needed for dice detection
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = Detector(
    dice_detection_model_path="models/best_detection_model.tflite",
    dice_score_model_path="models/best_score_model.tflite",
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
    except Exception:
        print("WebSocket error:")
        traceback.print_exc()
        await websocket.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
