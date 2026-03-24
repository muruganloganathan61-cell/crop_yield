"""
TensorFlow Model Export & Deployment Guide
===========================================
Exports trained plant disease classification model to multiple formats
for production use, sharing, and deployment.

Dataset: New Plant Diseases Dataset (38 classes)
Framework: TensorFlow 2.x / Keras
Project: Crop Yield Prediction
"""

import tensorflow as tf
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import os

# ============================================================================
# SECTION 1: SAVE MODEL IN SAVEDMODEL FORMAT
# ============================================================================

def save_as_savedmodel(model, export_dir='../exports/savedmodel'):
    """
    Save model in TensorFlow SavedModel format.
    
    This is the universal interchange format for TensorFlow models.
    Includes computation graph, weights, and serving signatures.
    """
    export_path = Path(export_dir)
    export_path.mkdir(parents=True, exist_ok=True)
    
    # Save the model
    model.save(str(export_path), save_format='tf')
    
    print(f"✓ SavedModel exported to: {export_path}")
    print(f"  Directory structure:")
    print(f"    - saved_model.pb (computation graph)")
    print(f"    - variables/ (model weights)")
    print(f"    - assets/ (additional files)")
    return str(export_path)


# ============================================================================
# SECTION 2: SAVE MODEL AS .KERAS SINGLE FILE
# ============================================================================

def save_as_keras(model, filepath='../exports/plant_disease_model.keras'):
    """
    Save model as single .keras file (recommended Keras format).
    
    This is the native Keras format - compact, self-contained, and includes
    everything needed to reconstruct the model.
    """
    file_path = Path(filepath)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save as .keras file
    model.save(str(file_path), save_format='keras')
    
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    print(f"✓ Keras model saved to: {file_path}")
    print(f"  File size: {file_size_mb:.2f} MB")
    print(f"  Contains: architecture + weights + optimizer state")
    return str(file_path)


# ============================================================================
# SECTION 3: CONVERT TO TENSORFLOW LITE
# ============================================================================

def convert_to_tflite(savedmodel_dir, output_file='../exports/plant_disease_model.tflite',
                      optimize=True):
    """
    Convert SavedModel to TensorFlow Lite format.
    
    Args:
        savedmodel_dir: Path to SavedModel directory
        output_file: Output .tflite file path
        optimize: Apply default optimizations (quantization)
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize converter from SavedModel
    converter = tf.lite.TFLiteConverter.from_saved_model(savedmodel_dir)
    
    if optimize:
        # Apply optimizations (reduces size, increases speed)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        print("  Applying dynamic range quantization...")
    
    # Convert the model
    tflite_model = converter.convert()
    
    # Save to file
    output_path.write_bytes(tflite_model)
    
    file_size_mb = len(tflite_model) / (1024 * 1024)
    print(f"✓ TFLite model saved to: {output_path}")
    print(f"  File size: {file_size_mb:.2f} MB")
    print(f"  Optimized: {optimize}")
    return str(output_path)


# ============================================================================
# SECTION 4: SAVE MODEL METADATA
# ============================================================================

def save_model_metadata(model, output_dir='../exports', dataset_info=None):
    """
    Save model metadata and configuration for documentation.
    
    Args:
        model: Trained Keras model
        output_dir: Directory to save metadata
        dataset_info: Dictionary with dataset information
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    metadata = {
        'timestamp': datetime.now().isoformat(),
        'framework': 'TensorFlow 2.x / Keras',
        'model_architecture': {
            'input_shape': model.input_shape,
            'output_shape': model.output_shape,
            'total_layers': len(model.layers),
            'total_parameters': int(model.count_params()),
            'trainable_parameters': sum([tf.size(w).numpy() for w in model.trainable_weights]),
        },
        'model_summary': str(model.summary()),
    }
    
    # Add dataset info if provided
    if dataset_info:
        metadata['dataset'] = dataset_info
    
    # Save to JSON
    metadata_file = output_path / 'model_metadata.json'
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    print(f"✓ Metadata saved to: {metadata_file}")
    return str(metadata_file)


# ============================================================================
# SECTION 5: LOAD AND INFERENCE EXAMPLES
# ============================================================================

def inference_from_savedmodel(savedmodel_dir, image_array):
    """
    Load SavedModel and run inference.
    
    Args:
        savedmodel_dir: Path to SavedModel directory
        image_array: Preprocessed image (numpy array)
    
    Returns:
        Predictions array
    """
    print("\n--- Loading from SavedModel ---")
    model = tf.keras.models.load_model(savedmodel_dir)
    predictions = model.predict(image_array, verbose=0)
    print(f"✓ Inference complete. Output shape: {predictions.shape}")
    return predictions


def inference_from_keras(keras_filepath, image_array):
    """
    Load .keras file and run inference.
    
    Args:
        keras_filepath: Path to .keras file
        image_array: Preprocessed image (numpy array)
    
    Returns:
        Predictions array
    """
    print("\n--- Loading from .keras file ---")
    model = tf.keras.models.load_model(keras_filepath)
    predictions = model.predict(image_array, verbose=0)
    print(f"✓ Inference complete. Output shape: {predictions.shape}")
    return predictions


def inference_from_tflite(tflite_filepath, image_array):
    """
    Load TFLite model and run inference.
    
    Args:
        tflite_filepath: Path to .tflite file
        image_array: Preprocessed image (numpy array, float32)
    
    Returns:
        Predictions array
    """
    print("\n--- Loading from TFLite ---")
    
    # Load TFLite model
    interpreter = tf.lite.Interpreter(model_path=tflite_filepath)
    interpreter.allocate_tensors()
    
    # Get input/output details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    # Set input tensor
    interpreter.set_tensor(input_details[0]['index'], image_array)
    
    # Run inference
    interpreter.invoke()
    
    # Get output tensor
    predictions = interpreter.get_tensor(output_details[0]['index'])
    print(f"✓ Inference complete. Output shape: {predictions.shape}")
    return predictions


# ============================================================================
# SECTION 6: COMPLETE EXPORT PIPELINE
# ============================================================================

def export_all_formats(model, base_dir='../exports', model_name='plant_disease_model'):
    """
    Export trained model to all formats in one go.
    
    Args:
        model: Trained Keras model
        base_dir: Base directory for all exports
        model_name: Name prefix for exported files
    
    Returns:
        Dictionary with paths to all exported formats
    """
    print("=" * 70)
    print("EXPORTING PLANT DISEASE MODEL TO ALL FORMATS")
    print("=" * 70)
    
    paths = {}
    
    # 1. SavedModel format
    print("\n[1/3] Exporting to SavedModel format...")
    paths['savedmodel'] = save_as_savedmodel(
        model, 
        export_dir=f'{base_dir}/savedmodel'
    )
    
    # 2. Keras format
    print("\n[2/3] Exporting to .keras format...")
    paths['keras'] = save_as_keras(
        model,
        filepath=f'{base_dir}/{model_name}.keras'
    )
    
    # 3. TFLite format
    print("\n[3/3] Converting to TensorFlow Lite...")
    paths['tflite'] = convert_to_tflite(
        paths['savedmodel'],
        output_file=f'{base_dir}/{model_name}.tflite',
        optimize=True
    )
    
    # 4. Save metadata
    print("\n[4/4] Saving model metadata...")
    dataset_info = {
        'name': 'New Plant Diseases Dataset (Augmented)',
        'path': '../New Plant Diseases Dataset(Augmented)',
        'classes': 38,
        'split': ['train', 'valid', 'test']
    }
    save_model_metadata(model, base_dir, dataset_info)
    
    print("\n" + "=" * 70)
    print("EXPORT COMPLETE!")
    print("=" * 70)
    print("\nExported files:")
    for format_name, path in paths.items():
        print(f"  {format_name:12s}: {path}")
    
    return paths


# ============================================================================
# SECTION 7: LOAD DATASET CLASSES
# ============================================================================

def get_plant_disease_classes(dataset_root='../New Plant Diseases Dataset(Augmented)/New Plant Diseases Dataset(Augmented)/train'):
    """
    Extract class names from dataset directory structure.
    
    Args:
        dataset_root: Root directory of training data
    
    Returns:
        List of class names
    """
    dataset_path = Path(dataset_root)
    if not dataset_path.exists():
        print(f"Warning: Dataset path not found: {dataset_root}")
        return None
    
    classes = sorted([d.name for d in dataset_path.iterdir() if d.is_dir()])
    print(f"Found {len(classes)} plant disease classes:")
    for i, cls in enumerate(classes, 1):
        print(f"  {i:2d}. {cls}")
    
    return classes


# ============================================================================
# SECTION 8: COMPLETE USAGE EXAMPLE
# ============================================================================

def main():
    """
    Complete example: export model and test inference from all formats.
    
    PREREQUISITE: You must have a trained model available.
    
    USAGE:
    1. Update 'model_path' to point to your trained model
    2. Run this script: python export_models.py
    """
    
    # STEP 1: Check and load plant disease classes
    print("Loading plant disease classes from dataset...")
    classes = get_plant_disease_classes()
    print(f"✓ Total classes: {len(classes)}\n")
    
    # STEP 2: Load your trained model
    model_path = 'plant_disease_model.keras'  # Update with your model path
    
    if not os.path.exists(model_path):
        print(f"\n⚠ Model not found at: {model_path}")
        print("To use this export script:")
        print(f"  1. Train your model using train_models.py")
        print(f"  2. Save it as '{model_path}'")
        print(f"  3. Update 'model_path' variable in main() function")
        return
    
    print("Loading trained model...")
    model = tf.keras.models.load_model(model_path)
    print(f"✓ Model loaded. Input shape: {model.input_shape}")
    print(f"  Number of classes: {model.output_shape[-1]}")
    
    # STEP 3: Export to all formats
    exported_paths = export_all_formats(model, base_dir='../exports')
    
    # STEP 4: Test inference from each format
    print("\n" + "=" * 70)
    print("TESTING INFERENCE FROM ALL FORMATS")
    print("=" * 70)
    
    # Create dummy input (replace with actual preprocessed image)
    # Assuming input shape is (224, 224, 3) - adjust as needed
    input_shape = model.input_shape[1:]  # Remove batch dimension
    dummy_image = np.random.random((1, *input_shape)).astype(np.float32)
    print(f"\nTest input shape: {dummy_image.shape}")
    
    # Test SavedModel
    preds_savedmodel = inference_from_savedmodel(
        exported_paths['savedmodel'], 
        dummy_image
    )
    
    # Test .keras
    preds_keras = inference_from_keras(
        exported_paths['keras'],
        dummy_image
    )
    
    # Test TFLite
    preds_tflite = inference_from_tflite(
        exported_paths['tflite'],
        dummy_image
    )
    
    # Verify outputs match
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    print(f"SavedModel vs Keras match: {np.allclose(preds_savedmodel, preds_keras)}")
    print(f"SavedModel vs TFLite match: {np.allclose(preds_savedmodel, preds_tflite, atol=1e-5)}")
    print("\nNote: Small differences in TFLite are expected due to quantization.")


# ============================================================================
# FORMAT SELECTION GUIDE
# ============================================================================

FORMAT_GUIDE = """
╔══════════════════════════════════════════════════════════════════════════╗
║                    FORMAT SELECTION GUIDE                                ║
╚══════════════════════════════════════════════════════════════════════════╝

┌─ SAVEDMODEL ─────────────────────────────────────────────────────────────┐
│ Use when:                                                                 │
│  ✓ Sharing with other developers for retraining                          │
│  ✓ Deploying to TensorFlow Serving                                       │
│  ✓ Converting to other formats (ONNX, CoreML, TFLite)                    │
│  ✓ Version control in production systems                                 │
│  ✓ Language interoperability (Java, C++, Go)                             │
│                                                                           │
│ Don't use when:                                                           │
│  ✗ Quick prototyping (too verbose)                                       │
│  ✗ Mobile deployment (use TFLite instead)                                │
│  ✗ Simple file sharing (use .keras instead)                              │
└───────────────────────────────────────────────────────────────────────────┘

┌─ .KERAS (SINGLE FILE) ───────────────────────────────────────────────────┐
│ Use when:                                                                 │
│  ✓ Sharing with Python/Keras developers                                  │
│  ✓ Version control (single file, easy to track)                          │
│  ✓ Quick distribution and loading                                        │
│  ✓ Checkpointing during training                                         │
│  ✓ Storing in cloud storage (S3, GCS)                                    │
│                                                                           │
│ Don't use when:                                                           │
│  ✗ Production serving infrastructure                                     │
│  ✗ Non-Python environments                                               │
│  ✗ Mobile/edge deployment                                                │
└───────────────────────────────────────────────────────────────────────────┘

┌─ TFLITE ─────────────────────────────────────────────────────────────────┐
│ Use when:                                                                 │
│  ✓ Android/iOS mobile apps                                               │
│  ✓ Raspberry Pi, Jetson Nano, edge devices                               │
│  ✓ Microcontrollers (Arduino, ESP32)                                     │
│  ✓ Low-latency inference required                                        │
│  ✓ Limited memory/compute resources                                      │
│                                                                           │
│ Don't use when:                                                           │
│  ✗ Training or fine-tuning (inference only)                              │
│  ✗ Server-side deployment (use SavedModel)                               │
│  ✗ Complex preprocessing required                                        │
│  ✗ Need full TensorFlow ops support                                      │
└───────────────────────────────────────────────────────────────────────────┘

RECOMMENDED WORKFLOW:
1. Save as .keras during development for quick iterations
2. Export to SavedModel when ready to share with team
3. Convert to TFLite for mobile/edge deployment

FILE SIZES (typical for plant disease model - 38 classes):
  SavedModel:  ~90-100 MB (directory with multiple files)
  .keras:      ~85-95 MB (single file)
  TFLite:      ~30-40 MB (quantized, single file)

QUICK START:
  python export_models.py       # Export model and run tests
  python export_models.py       # Print this guide
"""

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--info':
        print(FORMAT_GUIDE)
    else:
        print(FORMAT_GUIDE)
        print("\n" + "=" * 70)
        print("RUNNING EXPORT PIPELINE")
        print("=" * 70)
        main()
