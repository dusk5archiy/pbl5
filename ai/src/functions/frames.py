from PIL import Image
import numpy as np
import cv2


def similar_frames(frame1: Image.Image, frame2: Image.Image):
    def grayscale(frame):
        return cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2GRAY).astype(float)

    arr1 = grayscale(frame1)
    arr2 = grayscale(frame2)
    mse = np.mean((arr1 - arr2) ** 2)
    return 1 / (1 + mse / 255)
