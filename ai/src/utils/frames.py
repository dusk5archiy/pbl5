from PIL import Image
import numpy as np
from skimage.metrics import structural_similarity
from src.utils.image import to_grayscale

def similar_frames(frame1: Image.Image, frame2: Image.Image, threshold: float = 0.8) -> bool:
    if frame1.size != frame2.size:
        frame2 = frame2.resize(frame1.size, Image.Resampling.LANCZOS)
    
    arr1 = np.array(frame1)
    arr2 = np.array(frame2)
    arr1 = to_grayscale(arr1)
    arr2 = to_grayscale(arr2)

    ssim_score = structural_similarity(
        arr1, arr2,
        data_range=arr1.max() - arr1.min(),
        channel_axis=-1  # Last axis is the channel dimension
    )
    return ssim_score >= threshold