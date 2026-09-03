from pathlib import Path

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from liveness.model import LivenessModel


# ============================================================
# CONFIG
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "best_liveness_model.pth"
)

IMAGE_SIZE = 224

BATCH_SIZE = 8


# ============================================================
# DEVICE
# ============================================================

DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


print("=" * 60)
print("LIVENESS MODEL EVALUATION")
print("=" * 60)

print(
    f"\nDevice: {DEVICE}"
)


# ============================================================
# TRANSFORM
# ============================================================

test_transform = transforms.Compose([

    transforms.Resize(
        (IMAGE_SIZE, IMAGE_SIZE)
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[
            0.485,
            0.456,
            0.406
        ],
        std=[
            0.229,
            0.224,
            0.225
        ]
    )
])


# ============================================================
# TEST DATASET
# ============================================================

test_dataset = datasets.ImageFolder(
    DATA_DIR / "test",
    transform=test_transform
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0
)

print(
    f"Test images: {len(test_dataset)}"
)

print(
    f"Classes: {test_dataset.classes}"
)


# ============================================================
# LOAD MODEL
# ============================================================

model = LivenessModel(
    num_classes=2,
    pretrained=False
)

checkpoint = torch.load(
    MODEL_PATH,
    map_location=DEVICE
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(DEVICE)

model.eval()


print(
    f"\nLoaded model:"
)

print(MODEL_PATH)


# ============================================================
# PREDICTIONS
# ============================================================

all_labels = []

all_predictions = []

all_probabilities = []


with torch.no_grad():

    for images, labels in test_loader:

        images = images.to(DEVICE)

        outputs = model(images)

        probabilities = torch.softmax(
            outputs,
            dim=1
        )

        predictions = outputs.argmax(
            dim=1
        )

        all_labels.extend(
            labels.numpy()
        )

        all_predictions.extend(
            predictions.cpu().numpy()
        )

        all_probabilities.extend(
            probabilities[:, 1]
            .cpu()
            .numpy()
        )


# ============================================================
# STANDARD METRICS
# ============================================================

accuracy = accuracy_score(
    all_labels,
    all_predictions
)

precision = precision_score(
    all_labels,
    all_predictions,
    zero_division=0
)

recall = recall_score(
    all_labels,
    all_predictions,
    zero_division=0
)

f1 = f1_score(
    all_labels,
    all_predictions,
    zero_division=0
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    all_labels,
    all_predictions
)


# ============================================================
# PAD METRICS
# ============================================================

# Our labels:
#
# 0 = LIVE
# 1 = SPOOF
#
# Confusion matrix:
#
#             Pred LIVE   Pred SPOOF
# Actual LIVE
# Actual SPOOF


tn = cm[0][0]
fp = cm[0][1]

fn = cm[1][0]
tp = cm[1][1]


# ------------------------------------------------------------
# BPCER
# Bona Fide Presentation Classification Error Rate
#
# Percentage of genuine/live samples incorrectly
# classified as spoof.
# ------------------------------------------------------------

if (tn + fp) > 0:

    bpcer = fp / (tn + fp)

else:

    bpcer = 0.0


# ------------------------------------------------------------
# APCER
# Attack Presentation Classification Error Rate
#
# Percentage of spoof samples incorrectly
# classified as live.
# ------------------------------------------------------------

if (tp + fn) > 0:

    apcer = fn / (tp + fn)

else:

    apcer = 0.0


# ------------------------------------------------------------
# ACER
# Average Classification Error Rate
# ------------------------------------------------------------

acer = (
    apcer + bpcer
) / 2


# ============================================================
# PRINT RESULTS
# ============================================================

print("\n" + "=" * 60)

print("TEST RESULTS")

print("=" * 60)

print(
    f"\nAccuracy : "
    f"{accuracy:.4f}"
)

print(
    f"Precision: "
    f"{precision:.4f}"
)

print(
    f"Recall   : "
    f"{recall:.4f}"
)

print(
    f"F1 Score : "
    f"{f1:.4f}"
)


print("\n" + "-" * 60)

print("CONFUSION MATRIX")

print("-" * 60)

print(
    "              Pred LIVE   Pred SPOOF"
)

print(
    f"Actual LIVE      {tn:3d}          {fp:3d}"
)

print(
    f"Actual SPOOF     {fn:3d}          {tp:3d}"
)


print("\n" + "-" * 60)

print("PAD METRICS")

print("-" * 60)

print(
    f"APCER: {apcer:.4f}"
)

print(
    f"BPCER: {bpcer:.4f}"
)

print(
    f"ACER : {acer:.4f}"
)


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\n" + "-" * 60)

print("CLASSIFICATION REPORT")

print("-" * 60)

print(
    classification_report(
        all_labels,
        all_predictions,
        target_names=[
            "live",
            "spoof"
        ],
        zero_division=0
    )
)


# ============================================================
# COMPLETE
# ============================================================

print("=" * 60)

print("EVALUATION COMPLETE")

print("=" * 60)