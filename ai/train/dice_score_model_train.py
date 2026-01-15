from torch.utils.data import Dataset
from PIL import Image
import os
from torchvision import transforms
import concurrent.futures

inter_transform = transforms.Compose(
    [
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)


def process_sample(args):
    image_path, x, y, w, h, score = args
    img = Image.open(image_path).crop((x, y, x + w, y + h))
    img = img.resize((32, 32))

    label = int(score) - 1
    records = []

    variant_functs = [
        lambda x: x,
        lambda x: x.transpose(Image.FLIP_TOP_BOTTOM),  # type: ignore
        lambda x: x.transpose(Image.FLIP_LEFT_RIGHT),  # type: ignore
        lambda x: x.rotate(90),
    ]

    for vf in variant_functs:
        var_img = vf(img)
        img_tensor = inter_transform(var_img)
        records.append((img_tensor, label))

    return records


class ProjectDataset(Dataset):
    def __init__(self, input_dir, target_dir):
        self.input_dir = input_dir
        self.target_dir = target_dir
        self.records = []
        targets = []
        for target_file in os.listdir(target_dir):
            if not target_file.endswith(".txt"):
                continue
            base = os.path.splitext(target_file)[0]
            input_file = base + ".png"
            input_path = os.path.join(input_dir, input_file)
            target_path = os.path.join(target_dir, target_file)
            if not os.path.exists(input_path):
                continue
            with open(target_path, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) != 5:
                        continue
                    x, y, w, h, score = map(int, parts)
                    targets.append((input_path, x, y, w, h, score))

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for result in executor.map(process_sample, targets):
                self.records.extend(result)

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        return self.records[idx]


if __name__ == "__main__":
    pass
