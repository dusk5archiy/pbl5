#!/usr/bin/env python3
"""
Augment dataset with model predictions.

This script loads the dice_detection and dice_score models to predict
annotations for images that don't have manual annotations yet. The predictions
are saved as XXXXa.txt files (where XXXX is the image filename).

Example:
    For an image 0001.png without 0001.txt, creates 0001a.txt with predictions.
"""

import os
from pathlib import Path
from PIL import Image

from src.parse.config import load_config
from src.task.detector import Detector


def augment_folder(inputs_folder, targets_folder, detector):
    """
    Augment a single folder with model predictions.
    
    Args:
        inputs_folder (str): Path to inputs folder
        targets_folder (str): Path to targets folder
        detector: Detector instance for predictions
    """
    if not os.path.exists(inputs_folder):
        print(f"Warning: Inputs folder does not exist: {inputs_folder}")
        return
    
    # Ensure target directory exists
    os.makedirs(targets_folder, exist_ok=True)
    
    # Get all image files
    image_files = sorted([
        f for f in os.listdir(inputs_folder) 
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ])
    
    print(f"Processing {len(image_files)} images in {inputs_folder}...")
    
    augmented_count = 0
    for img_file in image_files:
        base = os.path.splitext(img_file)[0]
        txt_file = base + ".txt"
        augmented_txt_file = base + "a.txt"
        
        txt_path = os.path.join(targets_folder, txt_file)
        augmented_txt_path = os.path.join(targets_folder, augmented_txt_file)
        
        # Skip if manual annotation exists
        if os.path.exists(txt_path):
            continue
        
        # Load and predict
        img_path = os.path.join(inputs_folder, img_file)
        try:
            img = Image.open(img_path)
            bboxes, scores = detector(img)
            
            # Save predictions as XXXXa.txt
            with open(augmented_txt_path, 'w') as f:
                for bbox, score in zip(bboxes, scores):
                    x, y, w, h = bbox
                    f.write(f"{x} {y} {w} {h} {score}\n")
            
            augmented_count += 1
            print(f"  {img_file} -> {augmented_txt_file}")
        except Exception as e:
            print(f"  Error processing {img_file}: {e}")
    
    print(f"Augmented {augmented_count} images in {os.path.basename(inputs_folder)}")


def main():
    """Main function to augment dataset."""
    config = load_config(file_path="config/config.yml")
    dataset_base = Path(config.dataset_path)
    
    # Initialize detector
    dice_detection_config = config.tasks.dice_detection
    dice_score_config = config.tasks.dice_score
    
    detector = Detector(
        dice_detection_model_path=dice_detection_config.inference_path,
        dice_score_model_path=dice_score_config.inference_path,
        dice_detection_image_resolution=dice_detection_config.image_resolution,
        dice_score_image_resolution=dice_score_config.image_resolution,
        colored=config.colored,
    )
    
    inputs_dir = str(dataset_base / "inputs")
    targets_dir = str(dataset_base / "targets")
    
    # Get all numbered subfolders
    numbered_folders = sorted([
        d for d in os.listdir(inputs_dir)
        if os.path.isdir(os.path.join(inputs_dir, d)) and d.isdigit()
    ])
    
    print(f"Found {len(numbered_folders)} dataset folders: {numbered_folders}")
    print()
    
    # Process each numbered folder
    for folder_name in numbered_folders:
        inputs_subfolder = os.path.join(inputs_dir, folder_name)
        targets_subfolder = os.path.join(targets_dir, folder_name)
        augment_folder(inputs_subfolder, targets_subfolder, detector)
        print()
    
    print("✓ Augmentation complete!")


if __name__ == "__main__":
    main()
