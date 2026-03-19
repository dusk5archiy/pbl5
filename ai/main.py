from PIL import Image
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from colorama import Fore, init
from collections import Counter

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
        self.previous_frame: Image.Image | None = None  # Store only the previous frame
        self.previous_scores: Counter | None = None  # Store scores from previous frame
        self.consecutive_matches: int = (
            0  # Counter for consecutive frames with 2 dice and similarity
        )
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
    init()

    print(Fore.BLUE + "[--PENDING--] Waiting for a web socket...", Fore.RESET)
    await websocket.accept()
    print(Fore.CYAN + "[--SUCCESS--] Got a new socket.", Fore.RESET)
    connection_id = id(websocket)
    connection_states[connection_id] = ConnectionState()

    try:
        while True:
            print("Loop")
            # Receive image - get latest frame, skipping older queued frames
            data = await websocket.receive_bytes()

            # Drop stale frames: Keep only the most recent queued frame
            # This prevents processing old frames when detector is slower than frame send rate
            while True:
                try:
                    newer_data = await asyncio.wait_for(
                        websocket.receive_bytes(),
                        timeout=0.01,  # 10ms timeout to check for newer frames
                    )
                    data = newer_data
                except asyncio.TimeoutError:
                    break  # No more queued frames, continue with latest

            image = Image.open(io.BytesIO(data)).convert("RGB")

            state = connection_states[connection_id]
            state.frame_count += 1

            # Always run detector to get number of dice
            bboxes, scores = detector(image)
            print(Fore.MAGENTA + "Score detected", Counter(scores), Fore.RESET)
            num_dice = len(bboxes)

            # Only track frames with exactly 2 dice
            if num_dice != 2:
                # Reset counter - we need consecutive frames with 2 dice
                state.consecutive_matches = 0
                state.previous_frame = None
                state.previous_scores = None
                continue  # Don't send response, wait for next frame

            # Current frame has 2 dice - check similarity with previous frame
            is_similar_to_previous = False  # True for first frame with 2 dice
            has_same_scores = False  # True for first frame with 2 dice

            if state.previous_frame is not None:
                # Compare with previous frame
                similarity = similar_frames(image, state.previous_frame)
                is_similar_to_previous = (
                    similarity >= config.tasks.frame_detection.similarity_threshold
                )
                print(f"Similarity: {similarity:.3f}")

                # Check if scores are the same
                has_same_scores = Counter(scores) == state.previous_scores

            if is_similar_to_previous and has_same_scores:
                # Increment counter for consecutive match
                state.consecutive_matches += 1
            else:
                # Break in similarity or scores, reset counter
                state.consecutive_matches = 0

            print(f"Consecutive matches: {state.consecutive_matches}")
            # Update previous frame and scores for next comparison
            state.previous_frame = image
            state.previous_scores = Counter(scores)

            # Success: 2 consecutive frames with 2 dice are similar and have same scores
            if (
                state.consecutive_matches
                >= config.tasks.frame_detection.qualified_consecutive_frames - 1
            ):
                await websocket.send_json({"bboxes": bboxes, "scores": scores})

                # Reset state for next detection cycle
                state.consecutive_matches = 0
                state.previous_frame = None
                state.previous_scores = None
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
