from PIL import Image
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import io
import traceback
from src.task.detector import Detector
from src.parse.config import load_config

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = load_config("config/config.yml")

detector = Detector(
    dice_detection_model_path=config.tasks.dice_detection.inference_path,
    dice_score_model_path=config.tasks.dice_score.inference_path,
    dice_detection_image_resolution=config.tasks.dice_detection.image_resolution,
    dice_score_image_resolution=config.tasks.dice_score.image_resolution,
    colored=config.colored,
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
