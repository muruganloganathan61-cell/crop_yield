"""
Quick test to verify the training setup is correct
"""

import tensorflow as tf
from pathlib import Path
import os

print("=" * 70)
print("TRAINING SETUP VERIFICATION")
print("=" * 70)

# Check Python
print(f"\n[1] Python version: {os.sys.version}")

# Check TensorFlow
print(f"[2] TensorFlow version: {tf.__version__}")

# Check dataset
PROJECT_ROOT = Path(__file__).parent.parent
DATASET_DIR = PROJECT_ROOT / 'New Plant Diseases Dataset(Augmented)' / 'New Plant Diseases Dataset(Augmented)'
TRAIN_DIR = DATASET_DIR / 'train'
VALID_DIR = DATASET_DIR / 'valid'

print(f"\n[3] Dataset paths:")
print(f"    Project root: {PROJECT_ROOT}")
print(f"    Train dir exists: {TRAIN_DIR.exists()}")
print(f"    Valid dir exists: {VALID_DIR.exists()}")

if TRAIN_DIR.exists():
    train_classes = sorted([d.name for d in TRAIN_DIR.iterdir() if d.is_dir()])
    print(f"    Training classes: {len(train_classes)}")
    print(f"    First 5 classes: {train_classes[:5]}")

if VALID_DIR.exists():
    valid_classes = sorted([d.name for d in VALID_DIR.iterdir() if d.is_dir()])
    print(f"    Validation classes: {len(valid_classes)}")

# Check GPU
print(f"\n[4] GPU availability: {tf.config.list_physical_devices('GPU')}")

# Test data loading
print(f"\n[5] Testing data loading...")
try:
    train_ds = tf.keras.utils.image_dataset_from_directory(
        str(TRAIN_DIR),
        image_size=(224, 224),
        batch_size=32,
        label_mode='categorical'
    )
    print(f"    [OK] Successfully loaded training dataset")
    print(f"    Batch shape: {train_ds.element_spec[0].shape}")
    print(f"    Label shape: {train_ds.element_spec[1].shape}")
except Exception as e:
    print(f"    [ERROR] Failed to load dataset: {e}")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
print("\nTo start training, run:")
print("  cd G:\\crop yield prediction")
print("  python ml_models\\train_models.py")
print("\nNote: The first run will download the EfficientNetB0 model (~16MB)")
