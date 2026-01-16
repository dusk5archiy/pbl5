from PIL import Image
from .dice_score_model import DiceScoreModel
from torch.utils.data import DataLoader, random_split
from torch.utils.data import Dataset
from torchvision import transforms
import concurrent.futures
import os
import torch
import torch.nn as nn
import torch.optim as optim


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
        if not os.path.isdir(input_dir) or not os.path.isdir(target_dir):
            raise Exception("[-- ERROR --] The input and target folders must exist.")
        if not os.listdir(input_dir) or not os.listdir(target_dir):
            raise Exception(
                "[-- ERROR --] Both input and target folders must not be empty."
            )

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
    from tqdm import tqdm

    input_dir = "data/inputs"
    target_dir = "data/targets"

    dataset = ProjectDataset(input_dir=input_dir, target_dir=target_dir)

    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

    model = DiceScoreModel()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=1e-4)

    num_epochs = 25
    epoch_pbar = tqdm(range(num_epochs), desc="Training")
    for epoch in epoch_pbar:
        model.train()
        running_loss = 0.0
        for images, labels in tqdm(train_loader, leave=False):
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        avg_loss = running_loss / len(train_loader)

        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for images, labels in tqdm(val_loader, leave=False):
                outputs = model(images)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        acc = 100 * correct / total
        epoch_pbar.set_postfix({"Loss": f"{avg_loss:.4f}", "Acc": f"{acc:.2f}%"})

    output_model_path = "output/dice-score-model.pth"
    torch.save(model.state_dict(), output_model_path)
    print(f"[-- SUCCESS --] Model saved to {output_model_path}")
