import torch
import torch.nn as nn
from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights


class LivenessModel(nn.Module):
    """
    Lightweight CNN for binary facial liveness classification.

    Classes:
        0 -> LIVE
        1 -> SPOOF
    """

    def __init__(self, num_classes=2, pretrained=True):
        super().__init__()

        if pretrained:
            weights = MobileNet_V3_Small_Weights.DEFAULT
        else:
            weights = None

        self.backbone = mobilenet_v3_small(weights=weights)

        in_features = self.backbone.classifier[-1].in_features

        self.backbone.classifier[-1] = nn.Linear(
            in_features,
            num_classes
        )

    def forward(self, x):
        return self.backbone(x)


def create_model(device=None):

    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    model = LivenessModel(
        num_classes=2,
        pretrained=True
    )

    model = model.to(device)

    return model


if __name__ == "__main__":

    device = "cuda" if torch.cuda.is_available() else "cpu"

    model = create_model(device)

    dummy_input = torch.randn(
        1,
        3,
        224,
        224
    ).to(device)

    output = model(dummy_input)

    print("Device:", device)
    print("Output shape:", output.shape)