from pathlib import Path

import torch
from PIL import Image
from torchvision import transforms

from liveness.model import LivenessModel


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "best_liveness_model.pth"
)


# ============================================================
# DEVICE
# ============================================================

DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# IMAGE TRANSFORM
# ============================================================

TRANSFORM = transforms.Compose([

    transforms.Resize(
        (224, 224)
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
# LOAD MODEL
# ============================================================

def load_liveness_model():

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

    return model


# ============================================================
# PREDICT LIVENESS
# ============================================================

def predict_liveness(
    model,
    image
):

    """
    Predict whether an image is LIVE or SPOOF.

    Returns:

        label
        confidence
        live_probability
        spoof_probability
    """

    if not isinstance(image, Image.Image):

        image = Image.open(image)

    image = image.convert("RGB")

    tensor = TRANSFORM(image)

    tensor = tensor.unsqueeze(0)

    tensor = tensor.to(DEVICE)

    with torch.no_grad():

        outputs = model(tensor)

        probabilities = torch.softmax(
            outputs,
            dim=1
        )[0]

    live_probability = (
        probabilities[0].item()
    )

    spoof_probability = (
        probabilities[1].item()
    )

    if live_probability >= spoof_probability:

        label = "LIVE"

        confidence = live_probability

    else:

        label = "SPOOF"

        confidence = spoof_probability

    return {
        "label": label,
        "confidence": confidence,
        "live_probability": live_probability,
        "spoof_probability": spoof_probability
    }