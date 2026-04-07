from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
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
    
    # Recursively find all .txt files in target directories
    target_files = []
    for root, _, files in os.walk(target_dir_path):
        for file in files:
            if file.endswith(".txt"):
                target_files.append(os.path.join(root, file))
    
    result: list[DiceCrop] = []
    
    def read_txt_file(target_file_path):
        """Read a single txt file and return list of DiceCropData"""
        crops = []
        
        rel_path = os.path.relpath(target_file_path, target_dir_path)
        base = os.path.splitext(rel_path)[0]
        
        input_file_path = os.path.join(input_dir_path, base + ".png")

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
        for crops in executor.map(read_txt_file, target_files):
            result.extend(crops)
            
    return result
