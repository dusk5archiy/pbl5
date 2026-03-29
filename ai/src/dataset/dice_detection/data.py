import os
from concurrent.futures import ThreadPoolExecutor, as_completed

class ImageDetectionData:
    """Stores data for a single image with bounding boxes"""

    def __init__(self, input_file_path: str, bboxes: list[tuple[int, int, int, int]], scores: list[int]):
        self.input_file_path = input_file_path
        self.bboxes = bboxes
        self.scores = scores


def get_image_detection_datas(dataset_path: str, num_workers: int = 4) -> list[ImageDetectionData]:
    input_dir_path = os.path.join(dataset_path, "inputs")
    target_dir_path = os.path.join(dataset_path, "targets")
    target_files = [f for f in os.listdir(target_dir_path) if f.endswith(".txt")]
    result: list[ImageDetectionData] = []

    def read_image_data(target_file_name):
        """Read a single txt file and return ImageDetectionData"""
        base = os.path.splitext(target_file_name)[0]
        input_file_path = os.path.join(input_dir_path, base + ".png")
        target_file_path = os.path.join(target_dir_path, target_file_name)

        bboxes = []
        scores = []
        with open(target_file_path, encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                x, y, w, h, s = map(int, parts)
                bboxes.append((x, y, w, h))
                scores.append(s)

        return ImageDetectionData(
            input_file_path=input_file_path,
            bboxes=bboxes,
            scores=scores
        )

    # Parallel reading of txt files
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(read_image_data, f) for f in target_files]
        for future in as_completed(futures):
            result.append(future.result())

    return result