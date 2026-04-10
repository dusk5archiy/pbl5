import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from concurrent.futures import ThreadPoolExecutor, wait
import queue
import threading
import pickle
import os
from src.backend.logging import logger
from src.utils.image import generate_rotate_and_flip_images, process_pil_image, to_grayscale
from .data import ImageDetectionData
from tqdm import tqdm
from itertools import repeat, chain


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


class S7DatasetDiceDetection:
    def __init__(
        self,
        image_resolution: tuple[int, int],
        image_datas: list[ImageDetectionData],
        colored: bool,
        use_random: bool,
        cache_path: str | None = None,
        dataset_repeat: int = 1,
        queue_capacity: int = 500,
        num_workers: int = 4,
    ):
        self.num_workers = num_workers
        self.image_resolution = image_resolution
        self.colored = colored
        self.use_random = use_random
        self.queue_capacity = queue_capacity
        self.image_data = image_datas
        self.dataset_repeat = dataset_repeat
        self.cache_path = None if cache_path is None else cache_path + f"-{dataset_repeat}" + ".pkl"
        
        self.data_queue = queue.Queue(maxsize=queue_capacity)
        self.stop_loading = threading.Event()
        self.loading_thread = None
        self.cached_data = []

        self.rng = np.random.RandomState(seed=42 if not use_random else None)

        if not use_random:
            # Try to load from cache
            assert self.cache_path is not None
            if os.path.exists(self.cache_path):
                logger.info(f"Loading cached data from {self.cache_path}...")
                self.cached_data = self._load_cache()
            else:
                logger.info(f"Cache not found. Creating and saving to {self.cache_path}...")
                for img_data in tqdm(
                    chain.from_iterable(repeat(self.image_data, self.dataset_repeat)),
                    total=len(self.image_data) * self.dataset_repeat,
                ):
                    self.cached_data.extend(self._process_image_file(img_data))

                self.rng.shuffle(self.cached_data)
                self._save_cache(self.cached_data)

    def __len__(self):
        return len(self.cached_data)

    def _save_cache(self, data):
        assert self.cache_path is not None
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, 'wb') as f:
            pickle.dump(data, f)
        file_size_mb = os.path.getsize(self.cache_path) / (1024 * 1024)
        logger.success(f"Cache saved to {self.cache_path} ({file_size_mb:.2f} MB)")

    def _load_cache(self):
        assert self.cache_path is not None
        with open(self.cache_path, 'rb') as f:
            return pickle.load(f)

    def _process_image_file(self, image_data: ImageDetectionData):
        results = []

        with Image.open(image_data.input_file_path) as img:
            orig_width, orig_height = img.size
            img = process_pil_image(img, self.image_resolution)
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
            
            # Calculate maximum valid translation to keep bboxes in bounds
            if transformed_bboxes:
                min_x = min(x for x, y, w, h in transformed_bboxes)
                max_right = max(x + w for x, y, w, h in transformed_bboxes)
                min_y = min(y for x, y, w, h in transformed_bboxes)
                max_bottom = max(y + h for x, y, w, h in transformed_bboxes)
                
                # Calculate translation limits
                max_dx = new_width - max_right  # Can shift right up to this amount
                min_dx = -min_x  # Can shift left up to this amount
                max_dy = new_height - max_bottom  # Can shift down up to this amount
                min_dy = -min_y  # Can shift up up to this amount
                
                # Apply random translation within valid limits (use np.random for consistency)
                dx = int(self.rng.uniform(min_dx, max_dx))
                dy = int(self.rng.uniform(min_dy, max_dy))
            else:
                dx = dy = 0
            
            transformed_bboxes = [(x + dx, y + dy, w, h) for x, y, w, h in transformed_bboxes]
            # Negate dx, dy for PIL transform (opposite direction for image pixels)
            aug_img = aug_img.transform(aug_img.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy), fillcolor=(128, 128, 128)) # type: ignore
            
            brightness_factor = self.rng.uniform(0.01, 2.0)
            enhancer = ImageEnhance.Brightness(aug_img)
            aug_img = enhancer.enhance(brightness_factor)
            
            # Apply random blur augmentation
            blur_radius = self.rng.uniform(0, 2)
            aug_img = aug_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

            aug_np_img = np.array(aug_img)
            if not self.colored:
                aug_np_img = to_grayscale(aug_np_img)
            results.append((aug_np_img, transformed_bboxes))

        return results

    def generate_data(self):
        if not self.use_random:
            yield from self.cached_data
        else:
            with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                futures_set = set()
                
                for _ in range(self.dataset_repeat):
                    for image_data in self.image_data:
                        future = executor.submit(self._process_image_file, image_data)
                        futures_set.add(future)

                while futures_set:
                    if self.stop_loading.is_set():
                        break
                    
                    done, futures_set = wait(futures_set, return_when="FIRST_COMPLETED")

                    for future in done:
                        try:
                            results = future.result()
                            for result in results:
                                yield result
                        except Exception:
                            pass

    def _load_data_worker(self):
        try:
            for result in self.generate_data():
                self.data_queue.put(result)
        finally:
            self.data_queue.put(None)
            
    def clean_up(self):
        self.stop_loading.set()
        if self.loading_thread and self.loading_thread.is_alive():
            self.loading_thread.join(timeout=1.0)

    def __iter__(self):
        if not self.use_random:
            yield from self.cached_data
        else:
            self.data_queue = queue.Queue(maxsize=self.queue_capacity)
            self.stop_loading.clear()

            self.loading_thread = threading.Thread(
                target=self._load_data_worker, daemon=True
            )
            self.loading_thread.start()

            while True:
                item = self.data_queue.get()
                if item is None:
                    break
                
                yield item

            self.clean_up()

    def __del__(self):
        self.clean_up()


