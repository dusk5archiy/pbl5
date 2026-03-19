from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

class DiceCrop(BaseModel):
    """Stores data for a single dice crop"""

    input_file_path: str
    x: int
    y: int
    w: int
    h: int
    score: int



def get_dice_crops(dataset_path: str, num_workers: int=4) -> list[DiceCrop]:
    input_dir_path = os.path.join(dataset_path, "inputs")
    target_dir_path = os.path.join(dataset_path, "targets")
    target_files = [f for f in os.listdir(target_dir_path) if f.endswith(".txt")]
    result: list[DiceCrop] = []
    def read_txt_file(target_file_name):
        """Read a single txt file and return list of DiceCropData"""
        crops = []
        base = os.path.splitext(target_file_name)[0]
        input_file_path = os.path.join(input_dir_path, base + ".png")
        target_file_path = os.path.join(target_dir_path, target_file_name)

        with open(target_file_path, encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                x, y, w, h, score = map(int, parts)
                crops.append(
                    DiceCrop(
                        input_file_path=input_file_path,
                        x=x,
                        y=y,
                        w=w,
                        h=h,
                        score=score,
                    )
                )
        return crops

    # Parallel reading of txt files
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(read_txt_file, f) for f in target_files]
        for future in as_completed(futures):
            result.extend(future.result())
            
    return result
