from sklearn.metrics import precision_score, recall_score, f1_score
import numpy as np

def calc_clsfi_metrics(targets: np.ndarray, preds: np.ndarray):
    precision = precision_score(
        targets, preds, average="weighted", zero_division=0
    )
    recall = recall_score(
        targets, preds, average="weighted", zero_division=0
    )
    f1 = f1_score(targets, preds, average="weighted", zero_division=0)

    return float(precision), float(recall), float(f1)
