#!/usr/bin/env python3
"""
Remove all predicted annotation files (XXXXa.txt).

This script removes all files ending with 'a.txt' from the targets folder,
cleaning up predicted annotations while keeping manual annotations (XXXX.txt).
"""

import os
from pathlib import Path


def remove_predicted_files(targets_folder):
    """
    Remove all XXXXa.txt files from a targets folder.
    
    Args:
        targets_folder (str): Path to targets folder
    """
    if not os.path.exists(targets_folder):
        print(f"Warning: Targets folder does not exist: {targets_folder}")
        return
    
    removed_count = 0
    
    # Recursively find all XXXXa.txt files
    for root, dirs, files in os.walk(targets_folder):
        for file in files:
            if file.endswith("a.txt"):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    rel_path = os.path.relpath(file_path, targets_folder)
                    print(f"  Removed: {rel_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"  Error removing {file}: {e}")
    
    print(f"Removed {removed_count} predicted annotation files")


def main():
    """Main function to remove predicted annotations."""
    # Get the dataset path from config
    from src.parse.config import load_config
    
    config = load_config(file_path="config/config.yml")
    dataset_base = Path(config.dataset_path)
    
    targets_dir = str(dataset_base / "targets")
    
    print("Removing predicted annotation files (XXXXa.txt)...")
    print()
    
    remove_predicted_files(targets_dir)
    
    print()
    print("✓ Cleanup complete!")


if __name__ == "__main__":
    main()
