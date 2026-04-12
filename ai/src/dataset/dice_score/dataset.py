import threading
import queue
import pickle
import os
from src.utils.image import generate_rotate_and_flip_images, process_pil_image, to_grayscale
from concurrent.futures import ThreadPoolExecutor, wait
from tqdm import tqdm
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from itertools import repeat, chain
from src.backend.logging import logger

from .data import DiceCrop

class S7DatasetDiceScore:
    def __init__(
        self,
        dice_crops: list[DiceCrop],
        image_resolution: tuple[int, int],
        colored: bool,
        use_random: bool,
        queue_capacity: int = 1000,
        num_workers: int = 4,
        dataset_repeat: int = 1,
        cache_path: str | None = None,
    ):
        self.num_workers = num_workers
        self.image_resolution = image_resolution
        self.colored = colored
        self.use_random = use_random
        self.queue_capacity = queue_capacity

        self.data_queue = queue.Queue(maxsize=queue_capacity)
        self.stop_loading = threading.Event()
        self.loading_thread = None
        self.dice_crops = dice_crops
        self.cached_data = []
        self.dataset_repeat = dataset_repeat
        self.cache_path: str | None = None if cache_path is None else cache_path + f"-{dataset_repeat}" + ".pkl"

        self.rng = np.random.RandomState(seed=42 if not use_random else None)

        if not use_random:
            assert self.cache_path is not None
            if os.path.exists(self.cache_path):
                self.cached_data = self._load_cache()
            else:
                for results in [self._process_dice_crop(c) for c in tqdm(
                        chain.from_iterable(repeat(self.dice_crops, self.dataset_repeat)),
                        total=len(self.dice_crops) * self.dataset_repeat
                    )
                ]:
                    self.cached_data.extend(results)

                self.rng.shuffle(self.cached_data)
                self._save_cache(self.cached_data)
                
    def __len__(self):
        return len(self.cached_data)
                    
    def generate_data(self):
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures_set = set()
            
            for _ in range(self.dataset_repeat):
                for c in self.dice_crops:
                    future = executor.submit(self._process_dice_crop, c)
                    futures_set.add(future)

            while futures_set:
                if self.stop_loading.is_set():
                    break
                
                done, futures_set = wait(futures_set, return_when="FIRST_COMPLETED")

                for future in done:
                    yield from future.result()

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

    def _process_dice_crop(self, crop_data: DiceCrop):
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
            brightness_factor = self.rng.uniform(0.5, 1.5)
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(brightness_factor)
            blur_radius = self.rng.uniform(0, 1) 
            img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
            img_np = np.array(img)
            
            if not self.colored:
                img_np = to_grayscale(img_np)

            results.append((img_np, crop_data.score - 1))

        return results

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


