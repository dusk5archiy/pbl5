from concurrent.futures import ThreadPoolExecutor
import os

class ImageDetectionData:
    """Stores data for a single image with bounding boxes"""

    def __init__(self, input_file_path: str, bboxes: list[tuple[int, int, int, int]], scores: list[int]):
        self.input_file_path = input_file_path
        self.bboxes = bboxes
        self.scores = scores


def get_image_detection_datas(dataset_path: str, num_workers: int = 4) -> list[ImageDetectionData]:
    input_dir_path = os.path.join(dataset_path, "inputs")
    target_dir_path = os.path.join(dataset_path, "targets")
    
    target_files = []
    for root, _, files in os.walk(target_dir_path):
        for file in files:
            if file.endswith(".txt"):
                target_files.append(os.path.join(root, file))
    
    result: list[ImageDetectionData] = []

    def read_image_data(target_file_path):
        rel_path = os.path.relpath(target_file_path, target_dir_path)
        base = os.path.splitext(rel_path)[0]
        
        input_file_path = os.path.join(input_dir_path, base + ".png")

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
        for image_data in executor.map(read_image_data, target_files):
            result.append(image_data)

    return result