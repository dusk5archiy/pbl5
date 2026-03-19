import threading
import queue
from src.utils.image import generate_rotate_and_flip_images, process_pil_image, to_grayscale
from concurrent.futures import ThreadPoolExecutor, wait
import random
from PIL import Image, ImageEnhance
import numpy as np

from .data import DiceCrop

class S7DatasetDiceScore:
    def __init__(
        self,
        dice_crops: list[DiceCrop],
        image_resolution: tuple[int, int],
        colored: bool,
        queue_capacity: int = 1000,
        num_workers: int = 4,
    ):
        self.queue_capacity = queue_capacity
        self.num_workers = num_workers

        # Pre-load all data into pydantic models using parallel txt reading
        self.dice_crops = dice_crops
        # Queue for storing preprocessed data
        self.data_queue = queue.Queue(maxsize=queue_capacity)
        self.stop_loading = threading.Event()
        self.loading_thread = None
        
        self.image_resolution = image_resolution
        self.colored = colored

    def _process_dice_crop(self, crop_data: DiceCrop):
        """Process a single dice crop - for parallel execution"""
        results = []

        input_pil_file = Image.open(crop_data.input_file_path)
        input_pil_image = input_pil_file.crop(
            (
                crop_data.x,
                crop_data.y,
                crop_data.x + crop_data.w,
                crop_data.y + crop_data.h,
            )
        )
        input_pil_image = process_pil_image(
            input_pil_image, self.image_resolution
        )
        for img, _, _ in generate_rotate_and_flip_images(input_pil_image):
            # Randomly adjust luminosity from 50% to 200%
            brightness_factor = random.uniform(0.5, 2.0)
            enhancer = ImageEnhance.Brightness(img)
            img_adjusted = enhancer.enhance(brightness_factor)
            img_np = np.array(img_adjusted)
            
            if not self.colored:
                img_np = to_grayscale(img_np)

            results.append((img_np, crop_data.score - 1))

        return results

    def _load_data_worker(self):
        """Background worker that loads and preprocesses data into the queue using ThreadPoolExecutor"""
        try:
            with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                # Use a limited set of in-flight futures to control memory usage
                futures_set = set()
                crop_index = 0
                max_in_flight = (
                    self.num_workers * 2
                )  # Keep 2x workers worth of tasks in flight

                while crop_index < len(self.dice_crops) or futures_set:
                    # Submit new tasks up to max_in_flight limit
                    while len(futures_set) < max_in_flight and crop_index < len(
                        self.dice_crops
                    ):
                        if self.stop_loading.is_set():
                            break
                        crop_data = self.dice_crops[crop_index]
                        future = executor.submit(self._process_dice_crop, crop_data)
                        futures_set.add(future)
                        crop_index += 1

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


