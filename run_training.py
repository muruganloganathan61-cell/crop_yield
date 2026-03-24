"""
Simplified training runner - shows full output in the terminal
Run this to train the model with visible progress
"""

import subprocess
import sys

print("=" * 70)
print("PLANT DISEASE CLASSIFICATION TRAINING")
print("=" * 70)
print("\nStarting training... (this may take several hours)")
print("Training progress will be shown below:\n")

# Run the training script
result = subprocess.run(
    [sys.executable, 'ml_models/train_models.py'],
    cwd='.',
    text=True
)

sys.exit(result.returncode)
