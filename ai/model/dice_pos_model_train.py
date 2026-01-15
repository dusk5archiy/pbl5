from sklearn.model_selection import train_test_split
from ultralytics.models import YOLO
from PIL import Image
import os
import shutil


if __name__ == "__main__":
    # Convert Dataset to YOLO Format
    source_inputs = "data/inputs"
    source_targets = "data/targets"
    dest_dir = "yolo-data"

    # Create directories
    os.makedirs(f"{dest_dir}/images/train", exist_ok=True)
    os.makedirs(f"{dest_dir}/labels/train", exist_ok=True)
    os.makedirs(f"{dest_dir}/images/val", exist_ok=True)
    os.makedirs(f"{dest_dir}/labels/val", exist_ok=True)

    # Get all images and split
    image_files = [
        f for f in os.listdir(source_inputs) if f.endswith((".png", ".jpg", ".jpeg"))
    ]
    train_files, val_files = train_test_split(
        image_files, test_size=0.2, random_state=42
    )

    def convert_label_to_yolo_format(label_path, dest_label_path, image_path):
        img = Image.open(image_path)
        img_width, img_height = img.size

        with open(label_path, "r") as f:
            lines = f.readlines()

        yolo_lines = []
        for line in lines:
            x, y, w, h, _ = map(int, line.strip().split())
            x_center = (x + w / 2) / img_width
            y_center = (y + h / 2) / img_height
            w_norm = w / img_width
            h_norm = h / img_height
            yolo_lines.append(
                f"0 {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}"
            )

        with open(dest_label_path, "w") as f:
            f.write("\n".join(yolo_lines))

    # Process train
    print(f"Processing {len(train_files)} training images...")
    for img_file in train_files:
        base = os.path.splitext(img_file)[0]
        shutil.copy(
            f"{source_inputs}/{img_file}", f"{dest_dir}/images/train/{img_file}"
        )
        convert_label_to_yolo_format(
            f"{source_targets}/{base}.txt",
            f"{dest_dir}/labels/train/{base}.txt",
            f"{source_inputs}/{img_file}",
        )

    # Process val
    print(f"Processing {len(val_files)} validation images...")
    for img_file in val_files:
        base = os.path.splitext(img_file)[0]
        shutil.copy(f"{source_inputs}/{img_file}", f"{dest_dir}/images/val/{img_file}")
        convert_label_to_yolo_format(
            f"{source_targets}/{base}.txt",
            f"{dest_dir}/labels/val/{base}.txt",
            f"{source_inputs}/{img_file}",
        )

    print(f"✓ Dataset ready: {len(train_files)} train, {len(val_files)} val")

    model = YOLO()
    model.train(
        data="yolo-data/data.yaml",
        epochs=25,
        imgsz=256,
        batch=8,
        save=True,
        project="yolo-output",
        exist_ok=True,
    )
