from pathlib import Path

from PIL import Image
from torch.utils.data import Dataset


class LivenessDataset(Dataset):
    """
    Dataset for facial liveness detection.

    Expected structure:

    data/
        train/
            live/
                image1.jpg
                image2.jpg
            spoof/
                image1.jpg
                image2.jpg

        val/
            live/
            spoof/

        test/
            live/
            spoof/
    """

    CLASS_NAMES = {
        "live": 0,
        "spoof": 1
    }

    VALID_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp"
    }

    def __init__(self, root_dir, transform=None):
        self.root_dir = Path(root_dir)
        self.transform = transform

        self.samples = []

        for class_name, label in self.CLASS_NAMES.items():

            class_dir = self.root_dir / class_name

            if not class_dir.exists():
                continue

            for file_path in class_dir.rglob("*"):

                if file_path.suffix.lower() in self.VALID_EXTENSIONS:
                    self.samples.append(
                        (file_path, label)
                    )

        if not self.samples:
            raise RuntimeError(
                f"No images found in {self.root_dir}"
            )

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):

        image_path, label = self.samples[index]

        image = Image.open(image_path).convert("RGB")

        if self.transform:
            image = self.transform(image)

        return image, label