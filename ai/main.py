from PIL import Image
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import io
import traceback
from src.task.detector import Detector
from src.parse.config import load_config
from src.utils.frames import similar_frames

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = load_config("config/config.yml")

# Connection state management for frame stability detection
connection_states = {}

class ConnectionState:
    def __init__(self):
        self.previous_image: Image.Image | None = None
        self.frame_count: int = 0

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
    connection_id = id(websocket)
    connection_states[connection_id] = ConnectionState()

    try:
        while True:
            # Receive image
            data = await websocket.receive_bytes()
            image = Image.open(io.BytesIO(data)).convert("RGB")

            # Drop stale frames: Keep only the most recent queued frame
            # This prevents processing old frames when detector is slower than 500ms
            while True:
                try:
                    newer_data = await asyncio.wait_for(
                        websocket.receive_bytes(),
                        timeout=0.01  # 10ms timeout
                    )
                    data = newer_data
                    image = Image.open(io.BytesIO(data)).convert("RGB")
                except asyncio.TimeoutError:
                    break  # No more queued frames, continue with latest

            state = connection_states[connection_id]
            state.frame_count += 1

            # Always run detector to get number of dice
            bboxes, scores = detector(image)
            num_dice = len(bboxes)

            # Check if this is the first frame
            if state.previous_image is None:
                state.previous_image = image
                continue  # Don't send response, wait for next frame

            # Check if exactly 2 dice detected
            if num_dice != 2:
                state.previous_image = image
                continue  # Don't send response, wait for next frame

            # Check frame similarity
            if not similar_frames(state.previous_image, image, threshold=0.8):
                state.previous_image = image
                continue  # Not stable yet

            # Success: 2 dice detected and frames are stable
            await websocket.send_json({"bboxes": bboxes, "scores": scores})

            # Clear state for next detection cycle
            state.previous_image = None
            state.frame_count = 0

    except Exception:
        print("WebSocket error:")
        traceback.print_exc()
    finally:
        # Cleanup connection state
        if connection_id in connection_states:
            del connection_states[connection_id]
        await websocket.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
