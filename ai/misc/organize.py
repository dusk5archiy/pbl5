#!/usr/bin/env python3
"""
Organize dataset files by normalizing file names.

This script processes the datasets folder and:
1. Sorts files alphabetically in each numbered subfolder
2. Renames them using 4-digit numbers starting from 0001
3. Processes both inputs and targets folders

Example:
    For each folder (11, 12, 13, etc.):
    - inputs/11/: Sort files, rename to 0001.ext, 0002.ext, etc.
    - targets/11/: Sort files, rename to 0001.ext, 0002.ext, etc.
"""

import os
from pathlib import Path


def organize_folder(folder_path):
    """
    Organize files in a folder by sorting and renaming with 4-digit numbers.
    
    Args:
        folder_path (Path): Path to the folder containing files to organize
    """
    if not folder_path.exists():
        print(f"Warning: Folder does not exist: {folder_path}")
        return
    
    # Get all files (not directories) in the folder
    files = sorted([f for f in folder_path.iterdir() if f.is_file()])
    
    if not files:
        print(f"No files found in {folder_path}")
        return
    
    print(f"Organizing {folder_path} ({len(files)} files)...")
    
    # Rename each file with 4-digit number
    for index, file_path in enumerate(files, start=1):
        # Get file extension
        ext = file_path.suffix
        
        # Create new filename with 4-digit number
        new_name = f"{index:04d}{ext}"
        new_path = file_path.parent / new_name
        
        # Rename the file
        file_path.rename(new_path)
        print(f"  {file_path.name} -> {new_name}")


def main():
    """Main function to organize all dataset folders."""
    datasets_base = Path("/workspace/datasets/s7dataset-2-dice-detection")
    
    # Define input and target folders
    inputs_dir = datasets_base / "inputs"
    targets_dir = datasets_base / "targets"
    
    # Check if base directory exists
    if not datasets_base.exists():
        print(f"Error: Dataset base directory does not exist: {datasets_base}")
        return
    
    # Get all numbered subfolders (e.g., 11, 12, 13, etc.)
    if inputs_dir.exists():
        numbered_folders = sorted([
            d.name for d in inputs_dir.iterdir() 
            if d.is_dir() and d.name.isdigit()
        ])
    else:
        print(f"Error: Inputs directory does not exist: {inputs_dir}")
        return
    
    print(f"Found {len(numbered_folders)} numbered folders: {numbered_folders}")
    print()
    
    # Process each numbered folder in both inputs and targets
    for folder_name in numbered_folders:
        print(f"Processing folder '{folder_name}'...")
        
        # Organize inputs folder
        inputs_subfolder = inputs_dir / folder_name
        organize_folder(inputs_subfolder)
        
        # Organize targets folder
        targets_subfolder = targets_dir / folder_name
        organize_folder(targets_subfolder)
        
        print()
    
    print("✓ Organization complete!")


if __name__ == "__main__":
    main()
