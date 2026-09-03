from pathlib import Path
from PIL import Image
import random
import re


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATASET = PROJECT_ROOT / "raw_dataset" / "MSU-MFSD-master"

SOURCE_DIR = RAW_DATASET / "pics"

TRAIN_SUBJECT_FILE = RAW_DATASET / "train_sub_list.txt"
TEST_SUBJECT_FILE = RAW_DATASET / "test_sub_list.txt"

OUTPUT_DIR = PROJECT_ROOT / "data"

IMAGE_SIZE = (224, 224)

VAL_RATIO = 0.20

RANDOM_SEED = 42


# ============================================================
# SUBJECT LIST
# ============================================================

def read_subject_list(file_path):

    subjects = set()

    with open(file_path, "r", encoding="utf-8") as file:

        for line in file:

            value = line.strip()

            if not value:
                continue

            # Convert:
            # 01  -> 1
            # 02  -> 2
            # 11  -> 11

            subject_id = str(int(value))

            subjects.add(subject_id)

    return subjects


# ============================================================
# EXTRACT SUBJECT FROM FILENAME
# ============================================================

def extract_subject_id(filename):

    match = re.search(
        r"client(\d+)",
        filename,
        re.IGNORECASE
    )

    if not match:
        return None

    # client001 -> 1
    # client002 -> 2
    # client011 -> 11

    return str(int(match.group(1)))


# ============================================================
# CREATE DIRECTORIES
# ============================================================

def create_directories():

    directories = [

        OUTPUT_DIR / "train" / "live",
        OUTPUT_DIR / "train" / "spoof",

        OUTPUT_DIR / "val" / "live",
        OUTPUT_DIR / "val" / "spoof",

        OUTPUT_DIR / "test" / "live",
        OUTPUT_DIR / "test" / "spoof",

    ]

    for directory in directories:

        directory.mkdir(
            parents=True,
            exist_ok=True
        )


# ============================================================
# IMAGE PROCESSING
# ============================================================

def resize_and_save(
    source_path,
    destination_path
):

    try:

        image = Image.open(source_path)

        image = image.convert("RGB")

        image = image.resize(
            IMAGE_SIZE,
            Image.Resampling.LANCZOS
        )

        image.save(
            destination_path,
            quality=95
        )

        return True

    except Exception as error:

        print(
            f"ERROR: {source_path}"
        )

        print(error)

        return False


# ============================================================
# GET SOURCE IMAGES
# ============================================================

def get_images():

    images = []

    real_dir = SOURCE_DIR / "real"

    attack_dir = SOURCE_DIR / "attack"

    # -------------------------------
    # REAL
    # -------------------------------

    if real_dir.exists():

        for image_path in real_dir.glob("*.jpg"):

            images.append(
                (
                    image_path,
                    "live"
                )
            )

    # -------------------------------
    # ATTACK
    # -------------------------------

    if attack_dir.exists():

        for image_path in attack_dir.glob("*.jpg"):

            images.append(
                (
                    image_path,
                    "spoof"
                )
            )

    return images


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)

    print(
        "MSU-MFSD DATASET PREPARATION"
    )

    print("=" * 60)

    # --------------------------------------------------------
    # Check dataset
    # --------------------------------------------------------

    if not RAW_DATASET.exists():

        raise FileNotFoundError(
            f"Dataset not found:\n{RAW_DATASET}"
        )

    # --------------------------------------------------------
    # Read official subject lists
    # --------------------------------------------------------

    train_subjects = read_subject_list(
        TRAIN_SUBJECT_FILE
    )

    test_subjects = read_subject_list(
        TEST_SUBJECT_FILE
    )

    print(
        f"\nOfficial training subjects: "
        f"{len(train_subjects)}"
    )

    print(
        f"Official test subjects: "
        f"{len(test_subjects)}"
    )

    # --------------------------------------------------------
    # Split training subjects
    # --------------------------------------------------------

    training_subject_list = sorted(
        train_subjects,
        key=int
    )

    random.seed(RANDOM_SEED)

    shuffled = training_subject_list.copy()

    random.shuffle(shuffled)

    val_count = max(
        1,
        round(
            len(shuffled) * VAL_RATIO
        )
    )

    val_subjects = set(
        shuffled[:val_count]
    )

    final_train_subjects = set(
        shuffled[val_count:]
    )

    print(
        f"Training subjects: "
        f"{len(final_train_subjects)}"
    )

    print(
        f"Validation subjects: "
        f"{len(val_subjects)}"
    )

    print(
        f"Test subjects: "
        f"{len(test_subjects)}"
    )

    # --------------------------------------------------------
    # Print IDs for verification
    # --------------------------------------------------------

    print(
        "\nTrain subjects:"
    )

    print(
        sorted(
            final_train_subjects,
            key=int
        )
    )

    print(
        "\nValidation subjects:"
    )

    print(
        sorted(
            val_subjects,
            key=int
        )
    )

    print(
        "\nTest subjects:"
    )

    print(
        sorted(
            test_subjects,
            key=int
        )
    )

    # --------------------------------------------------------
    # Create output directories
    # --------------------------------------------------------

    create_directories()

    # --------------------------------------------------------
    # Get images
    # --------------------------------------------------------

    images = get_images()

    print(
        f"\nFound {len(images)} source images."
    )

    # --------------------------------------------------------
    # Counters
    # --------------------------------------------------------

    counters = {

        "train_live": 0,
        "train_spoof": 0,

        "val_live": 0,
        "val_spoof": 0,

        "test_live": 0,
        "test_spoof": 0,

        "skipped": 0

    }

    # --------------------------------------------------------
    # Process images
    # --------------------------------------------------------

    for source_path, label in images:

        filename = source_path.name

        subject_id = extract_subject_id(
            filename
        )

        if subject_id is None:

            print(
                f"Could not identify subject: "
                f"{filename}"
            )

            counters["skipped"] += 1

            continue

        # ----------------------------------------------------
        # Determine split
        # ----------------------------------------------------

        if subject_id in test_subjects:

            split = "test"

        elif subject_id in val_subjects:

            split = "val"

        elif subject_id in final_train_subjects:

            split = "train"

        else:

            print(
                f"Skipping subject {subject_id}: "
                f"not present in split lists."
            )

            counters["skipped"] += 1

            continue

        # ----------------------------------------------------
        # Destination
        # ----------------------------------------------------

        destination_dir = (
            OUTPUT_DIR
            / split
            / label
        )

        destination_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        destination_path = (
            destination_dir
            / filename
        )

        # ----------------------------------------------------
        # Process
        # ----------------------------------------------------

        success = resize_and_save(
            source_path,
            destination_path
        )

        if success:

            counter_key = (
                f"{split}_{label}"
            )

            counters[counter_key] += 1

    # --------------------------------------------------------
    # Final results
    # --------------------------------------------------------

    print("\n")

    print("=" * 60)

    print(
        "DATASET PREPARATION COMPLETE"
    )

    print("=" * 60)

    print(
        f"\nTrain LIVE   : "
        f"{counters['train_live']}"
    )

    print(
        f"Train SPOOF  : "
        f"{counters['train_spoof']}"
    )

    print(
        f"Val LIVE     : "
        f"{counters['val_live']}"
    )

    print(
        f"Val SPOOF    : "
        f"{counters['val_spoof']}"
    )

    print(
        f"Test LIVE    : "
        f"{counters['test_live']}"
    )

    print(
        f"Test SPOOF   : "
        f"{counters['test_spoof']}"
    )

    print(
        f"Skipped      : "
        f"{counters['skipped']}"
    )

    print(
        f"\nOutput directory:"
    )

    print(
        OUTPUT_DIR
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()