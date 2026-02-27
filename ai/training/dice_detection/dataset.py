import random
import numpy as np
from PIL import Image, ImageEnhance
from concurrent.futures import ThreadPoolExecutor, wait
from pydantic import BaseModel
import queue
import threading
from ults.image import generate_rotate_and_flip_images, process_pil_image
from .data import ImageDetectionData, get_image_detection_datas


def transform_bbox(
    bbox: tuple[int, int, int, int],
    rot: int,
    flip: str,
    img_width: int,
    img_height: int,
) -> tuple[int, int, int, int]:
    x, y, w, h = bbox
    # Apply rotation
    if rot == 90:
        new_x = y
        new_y = img_width - x - w
        new_w = h
        new_h = w
    elif rot == 180:
        new_x = img_width - x - w
        new_y = img_height - y - h
        new_w = w
        new_h = h
    elif rot == 270:
        new_x = img_height - y - h
        new_y = x
        new_w = h
        new_h = w
    else:
        new_x, new_y, new_w, new_h = x, y, w, h

    # Apply flip
    if flip == "horizontal":
        new_x = img_width - new_x - new_w
    elif flip == "vertical":
        new_y = img_height - new_y - new_h

    return (int(new_x), int(new_y), int(new_w), int(new_h))


class S7DatasetDiceDetectionConfig(BaseModel):
    dataset_path: str
    image_resolution: tuple[int, int] = (640, 480)


class S7DatasetDiceDetection:
    def __init__(
        self,
        config: S7DatasetDiceDetectionConfig,
        image_datas: list[ImageDetectionData] | None = None,
        queue_capacity: int = 500,
        num_workers: int = 4,
    ):
        self.config = config
        self.queue_capacity = queue_capacity
        self.num_workers = num_workers
        # Use pre-loaded data if provided, otherwise load from dataset_path
        if image_datas is not None:
            self.image_data = image_datas
        else:
            self.image_data: list[ImageDetectionData] = get_image_detection_datas(
                dataset_path=config.dataset_path, num_workers=num_workers
            )

        # Queue for storing preprocessed data
        self.data_queue = queue.Queue(maxsize=queue_capacity)
        self.stop_loading = threading.Event()
        self.loading_thread = None

    def _process_image_file(self, image_data: ImageDetectionData):
        """Process a single image file with its bboxes - for parallel execution"""
        results = []

        img = Image.open(image_data.input_file_path)
        orig_width, orig_height = img.size
        img = process_pil_image(img, self.config.image_resolution)
        new_width, new_height = img.size
        scale_x = new_width / orig_width
        scale_y = new_height / orig_height

        # Scale bboxes (already loaded in image_data)
        bboxes : list[tuple[int, int, int, int]] = []
        for x, y, w, h in image_data.bboxes:
            x = int(x * scale_x)
            y = int(y * scale_y)
            w = int(w * scale_x)
            h = int(h * scale_y)
            bboxes.append((x, y, w, h))

        # Augment using the generator
        for aug_img, rot, flip in generate_rotate_and_flip_images(img):
            transformed_bboxes = [
                transform_bbox(bbox, rot, flip, new_width, new_height)
                for bbox in bboxes
            ]
            # Add random shift
            dx = int(random.randint(-5, 5) / 100 * new_width)
            dy = int(random.randint(-5, 5) / 100 * new_height)
            transformed_bboxes = [(x - dx, y - dy, w, h) for x, y, w, h in transformed_bboxes]
            aug_img = aug_img.transform(aug_img.size, Image.AFFINE, (1, 0, dx, 0, 1, dy), fillcolor=(0, 0, 0)) # type: ignore
            # Apply random brightness augmentation
            brightness_factor = random.uniform(0.5, 2.0)
            enhancer = ImageEnhance.Brightness(aug_img)
            aug_img = enhancer.enhance(brightness_factor)

            aug_np_img = np.array(aug_img)
            results.append((aug_np_img, transformed_bboxes))

        return results

    def _load_data_worker(self):
        """Background worker that loads and preprocesses data into the queue using ThreadPoolExecutor"""
        try:
            with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                # Use a limited set of in-flight futures to control memory usage
                futures_set = set()
                image_index = 0
                max_in_flight = (
                    self.num_workers * 2
                )  # Keep 2x workers worth of tasks in flight

                while image_index < len(self.image_data) or futures_set:
                    # Submit new tasks up to max_in_flight limit
                    while len(futures_set) < max_in_flight and image_index < len(
                        self.image_data
                    ):
                        if self.stop_loading.is_set():
                            break
                        image_data = self.image_data[image_index]
                        future = executor.submit(self._process_image_file, image_data)
                        futures_set.add(future)
                        image_index += 1

                    if not futures_set:
                        break

                    # Wait for at least one future to complete
                    done, futures_set = wait(futures_set, return_when="FIRST_COMPLETED")

                    # Process completed futures
                    for future in done:
                        if self.stop_loading.is_set():
                            break
                        try:
                            results = future.result()
                            for result in results:
                                self.data_queue.put(result)
                        except Exception as e:
                            # Skip failed tasks
                            pass
        finally:
            # Signal end of data
            self.data_queue.put(None)

    def __iter__(self):
        # Reset the queue and stop flag
        self.data_queue = queue.Queue(maxsize=self.queue_capacity)
        self.stop_loading.clear()

        # Start background loading thread
        self.loading_thread = threading.Thread(
            target=self._load_data_worker, daemon=True
        )
        self.loading_thread.start()

        # Yield items from queue
        while True:
            item = self.data_queue.get()
            if item is None:  # End of data signal
                break
            yield item

        # Clean up
        self.stop_loading.set()
        if self.loading_thread and self.loading_thread.is_alive():
            self.loading_thread.join(timeout=1.0)

    def __del__(self):
        """Cleanup when object is destroyed"""
        self.stop_loading.set()
        if self.loading_thread and self.loading_thread.is_alive():
            self.loading_thread.join(timeout=1.0)

