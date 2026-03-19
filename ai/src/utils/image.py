import numpy as np
from PIL import Image
from typing import Generator
from hashlib import md5


def generate_rotate_and_flip_images(
    pil_image: Image.Image,
) -> Generator[tuple[Image.Image, int, str], None, None]:
    seen_hashes = set()

    ROTATIONS = [0, 180]
    if pil_image.width == pil_image.height:
        ROTATIONS.extend([90, 270])
    FLIPS = ["none", "horizontal", "vertical"]

    for rot in ROTATIONS:
        for flip in FLIPS:
            img = pil_image.rotate(rot)

            if flip == "horizontal":
                img = img.transpose(Image.FLIP_LEFT_RIGHT)  # type: ignore
            elif flip == "vertical":
                img = img.transpose(Image.FLIP_TOP_BOTTOM)  # type: ignore

            # Convert to numpy array
            img_array = np.array(img)

            # Create hash for uniqueness check
            img_hash = md5(img_array.tobytes()).hexdigest()

            # Only add if not seen before
            if img_hash not in seen_hashes:
                seen_hashes.add(img_hash)
                yield img, rot, flip


def process_pil_image(pil_image: Image.Image, dest_resolution: tuple[int, int]):
    pil_image = pil_image.resize(dest_resolution)
    return pil_image


def to_grayscale(image: np.ndarray) -> np.ndarray:
    if len(image.shape) == 3 and image.shape[2] == 3:
        # Convert RGB to grayscale using standard formula
        gray = np.dot(image[..., :3], [0.299, 0.587, 0.114])
        gray = gray.astype(np.uint8)
        return np.expand_dims(gray, axis=-1)
    return image

