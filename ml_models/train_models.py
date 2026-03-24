"""
Plant Disease Classification Model Training Pipeline
=====================================================
Complete production-ready training pipeline for the New Plant Diseases Dataset
with transfer learning, data augmentation, and best practices.

Dataset: https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset
Classes: 38 plant disease categories
Framework: TensorFlow 2.x / Keras
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.applications import EfficientNetB0, MobileNetV2, ResNet50V2
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Training configuration parameters"""
    
    # Dataset paths - automatically find the dataset
    import os
    # Get the project root (two directories up from ml_models)
    PROJECT_ROOT = Path(__file__).parent.parent
    DATASET_DIR = PROJECT_ROOT / 'New Plant Diseases Dataset(Augmented)' / 'New Plant Diseases Dataset(Augmented)'
    TRAIN_DIR = str(DATASET_DIR / 'train')
    VALID_DIR = str(DATASET_DIR / 'valid')
    
    # Image parameters
    IMG_SIZE = (224, 224)
    IMG_HEIGHT = 224
    IMG_WIDTH = 224
    BATCH_SIZE = 16  # Reduced for better CPU performance; increase to 32 if GPU available
    
    # Training parameters
    EPOCHS = 30
    INITIAL_LEARNING_RATE = 0.001
    NUM_CLASSES = 38
    
    # Model selection: 'efficientnet', 'mobilenet', or 'resnet'
    BASE_MODEL = 'efficientnet'
    
    # Output
    MODEL_SAVE_PATH = 'plant_disease_model.keras'
    HISTORY_SAVE_PATH = 'training_history.npy'


# ============================================================================
# DATA LOADING AND PREPROCESSING
# ============================================================================

def create_data_generators(config):
    """
    Create training and validation data generators with augmentation.
    
    Args:
        config: Configuration object
        
    Returns:
        train_dataset, val_dataset, class_names
    """
    print("=" * 70)
    print("LOADING DATASET")
    print("=" * 70)
    
    # Check if dataset paths exist
    train_path = Path(config.TRAIN_DIR)
    valid_path = Path(config.VALID_DIR)
    
    if not train_path.exists():
        print(f"✗ ERROR: Training dataset not found at: {train_path}")
        print(f"  Please ensure the dataset is extracted to:")
        print(f"  {train_path.parent.parent}")
        raise FileNotFoundError(f"Dataset not found at {train_path}")
    
    if not valid_path.exists():
        print(f"✗ ERROR: Validation dataset not found at: {valid_path}")
        raise FileNotFoundError(f"Validation dataset not found at {valid_path}")
    
    print(f"[OK] Dataset found at: {train_path.parent.parent}")
    
    # Data augmentation for training (improves generalization)
    train_datagen = keras.preprocessing.image.ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    # Only rescaling for validation (no augmentation)
    val_datagen = keras.preprocessing.image.ImageDataGenerator(
        rescale=1./255
    )
    
    # Load training data
    train_generator = train_datagen.flow_from_directory(
        config.TRAIN_DIR,
        target_size=config.IMG_SIZE,
        batch_size=config.BATCH_SIZE,
        class_mode='categorical',
        shuffle=True,
        seed=42
    )
    
    # Load validation data
    val_generator = val_datagen.flow_from_directory(
        config.VALID_DIR,
        target_size=config.IMG_SIZE,
        batch_size=config.BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )
    
    class_names = list(train_generator.class_indices.keys())
    
    print(f"\n[OK] Training samples: {train_generator.samples}")
    print(f"[OK] Validation samples: {val_generator.samples}")
    print(f"[OK] Number of classes: {len(class_names)}")
    print(f"[OK] Batch size: {config.BATCH_SIZE}")
    print(f"[OK] Image size: {config.IMG_SIZE}")
    
    return train_generator, val_generator, class_names


def create_tf_datasets(config):
    """
    Alternative: Create tf.data.Dataset pipelines (more performant).
    Use this if you want better performance with prefetching and caching.
    
    Args:
        config: Configuration object
        
    Returns:
        train_dataset, val_dataset, class_names
    """
    print("=" * 70)
    print("LOADING DATASET (tf.data pipeline)")
    print("=" * 70)
    
    # Load datasets
    train_ds = tf.keras.utils.image_dataset_from_directory(
        config.TRAIN_DIR,
        image_size=config.IMG_SIZE,
        batch_size=config.BATCH_SIZE,
        label_mode='categorical',
        shuffle=True,
        seed=42
    )
    
    val_ds = tf.keras.utils.image_dataset_from_directory(
        config.VALID_DIR,
        image_size=config.IMG_SIZE,
        batch_size=config.BATCH_SIZE,
        label_mode='categorical',
        shuffle=False
    )
    
    class_names = train_ds.class_names
    
    # Data augmentation layer
    data_augmentation = keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.2),
    ])
    
    # Normalization layer
    normalization = layers.Rescaling(1./255)
    
    # Apply augmentation to training data
    train_ds = train_ds.map(
        lambda x, y: (data_augmentation(normalization(x), training=True), y),
        num_parallel_calls=tf.data.AUTOTUNE
    )
    
    # Only normalize validation data
    val_ds = val_ds.map(
        lambda x, y: (normalization(x), y),
        num_parallel_calls=tf.data.AUTOTUNE
    )
    
    # Performance optimization
    train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=tf.data.AUTOTUNE)
    
    print(f"\n[OK] Number of classes: {len(class_names)}")
    print(f"[OK] Batch size: {config.BATCH_SIZE}")
    print(f"[OK] Image size: {config.IMG_SIZE}")
    print(f"[OK] Datasets optimized with prefetching and caching")
    
    return train_ds, val_ds, class_names


# ============================================================================
# MODEL ARCHITECTURE
# ============================================================================

def build_model(config, num_classes):
    """
    Build transfer learning model with pre-trained base.
    
    Args:
        config: Configuration object
        num_classes: Number of output classes
        
    Returns:
        Compiled Keras model
    """
    print("\n" + "=" * 70)
    print("BUILDING MODEL")
    print("=" * 70)
    
    # Select base model
    if config.BASE_MODEL == 'efficientnet':
        base_model = EfficientNetB0(
            include_top=False,
            weights='imagenet',
            input_shape=(config.IMG_HEIGHT, config.IMG_WIDTH, 3)
        )
        print("Base model: EfficientNetB0")
    elif config.BASE_MODEL == 'mobilenet':
        base_model = MobileNetV2(
            include_top=False,
            weights='imagenet',
            input_shape=(config.IMG_HEIGHT, config.IMG_WIDTH, 3)
        )
        print("Base model: MobileNetV2")
    elif config.BASE_MODEL == 'resnet':
        base_model = ResNet50V2(
            include_top=False,
            weights='imagenet',
            input_shape=(config.IMG_HEIGHT, config.IMG_WIDTH, 3)
        )
        print("Base model: ResNet50V2")
    else:
        raise ValueError(f"Unknown base model: {config.BASE_MODEL}")
    
    # Freeze base model initially
    base_model.trainable = False
    
    # Build complete model
    model = models.Sequential([
        layers.Input(shape=(config.IMG_HEIGHT, config.IMG_WIDTH, 3)),
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation='softmax')
    ], name='plant_disease_classifier')
    
    # Compile model
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=config.INITIAL_LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.TopKCategoricalAccuracy(k=3, name='top_3_accuracy')]
    )
    
    print(f"\n[OK] Model built successfully")
    print(f"  Total parameters: {model.count_params():,}")
    print(f"  Trainable parameters: {sum([tf.size(w).numpy() for w in model.trainable_weights]):,}")
    print(f"  Non-trainable parameters: {sum([tf.size(w).numpy() for w in model.non_trainable_weights]):,}")
    
    return model
# TRAINING CALLBACKS
# ============================================================================

def get_callbacks(config):
    """
    Create training callbacks for model checkpointing, early stopping, etc.
    
    Args:
        config: Configuration object
        
    Returns:
        List of Keras callbacks
    """
    # Create model directory
    Path(config.MODEL_SAVE_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    callbacks = [
        # Save best model
        ModelCheckpoint(
            filepath=config.MODEL_SAVE_PATH,
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        ),
        
        # Stop if no improvement
        EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        
        # Reduce learning rate on plateau
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1
        )
    ]
    
    return callbacks


# ============================================================================
# TRAINING PIPELINE
# ============================================================================

def train_model(config):
    """
    Complete training pipeline.
    
    Args:
        config: Configuration object
        
    Returns:
        trained_model, history, class_names
    """
    # Load data (choose one method)
    # Method 1: ImageDataGenerator (simpler, good for most cases)
    train_data, val_data, class_names = create_data_generators(config)
    
    # Method 2: tf.data (more performant, recommended for large datasets)
    # train_data, val_data, class_names = create_tf_datasets(config)
    
    # Build model
    model = build_model(config, num_classes=len(class_names))
    
    # Display model architecture
    print("\n" + "=" * 70)
    print("MODEL ARCHITECTURE")
    print("=" * 70)
    model.summary()
    
    # Get callbacks
    callbacks = get_callbacks(config)
    
    # Train model
    print("\n" + "=" * 70)
    print("TRAINING")
    print("=" * 70)
    
    history = model.fit(
        train_data,
        validation_data=val_data,
        epochs=config.EPOCHS,
        callbacks=callbacks,
        verbose=1
    )
    
    # Save training history
    np.save(config.HISTORY_SAVE_PATH, history.history)
    print(f"\n[OK] Training history saved to: {config.HISTORY_SAVE_PATH}")
    
    return model, history, class_names


# ============================================================================
# FINE-TUNING (OPTIONAL)
# ============================================================================

def fine_tune_model(model, train_data, val_data, config, unfreeze_layers=50):
    """
    Fine-tune the model by unfreezing some layers of the base model.
    Call this after initial training for better performance.
    
    Args:
        model: Trained model
        train_data: Training dataset
        val_data: Validation dataset
        config: Configuration object
        unfreeze_layers: Number of layers to unfreeze from the end
        
    Returns:
        fine_tuned_model, history
    """
    print("\n" + "=" * 70)
    print("FINE-TUNING MODEL")
    print("=" * 70)
    
    # Unfreeze the base model
    base_model = model.layers[0]
    base_model.trainable = True
    
    # Freeze all layers except the last N
    for layer in base_model.layers[:-unfreeze_layers]:
        layer.trainable = False
    
    # Recompile with lower learning rate
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=config.INITIAL_LEARNING_RATE * 0.1),
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.TopKCategoricalAccuracy(k=3, name='top_3_accuracy')]
    )
    
    print(f"[OK] Unfroze last {unfreeze_layers} layers")
    print(f"  Trainable parameters: {sum([tf.size(w).numpy() for w in model.trainable_weights]):,}")
    
    # Fine-tune
    fine_tune_epochs = 10
    history = model.fit(
        train_data,
        validation_data=val_data,
        epochs=fine_tune_epochs,
        callbacks=get_callbacks(config),
        verbose=1
    )
    
    return model, history


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_training_history(history, save_path='training_plots.png'):
    """
    Plot training and validation metrics.
    
    Args:
        history: Training history object
        save_path: Path to save the plot
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot accuracy
    axes[0].plot(history.history['accuracy'], label='Train Accuracy')
    axes[0].plot(history.history['val_accuracy'], label='Val Accuracy')
    axes[0].set_title('Model Accuracy', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Accuracy')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plot loss
    axes[1].plot(history.history['loss'], label='Train Loss')
    axes[1].plot(history.history['val_loss'], label='Val Loss')
    axes[1].set_title('Model Loss', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Loss')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"[OK] Training plots saved to: {save_path}")
    plt.show()


# ============================================================================
# EVALUATION
# ============================================================================

def evaluate_model(model, val_data):
    """
    Evaluate model on validation data.
    
    Args:
        model: Trained model
        val_data: Validation dataset
    """
    print("\n" + "=" * 70)
    print("MODEL EVALUATION")
    print("=" * 70)
    
    results = model.evaluate(val_data, verbose=1)
    
    print(f"\n[OK] Validation Loss: {results[0]:.4f}")
    print(f"[OK] Validation Accuracy: {results[1]:.4f} ({results[1]*100:.2f}%)")
    print(f"[OK] Top-3 Accuracy: {results[2]:.4f} ({results[2]*100:.2f}%)")


# ============================================================================
# MAIN TRAINING SCRIPT
# ============================================================================

def main():
    """
    Main training pipeline execution.
    """
    # Initialize configuration
    config = Config()
    
    print("\n" + "=" * 70)
    print("PLANT DISEASE CLASSIFICATION - TRAINING PIPELINE")
    print("=" * 70)
    print(f"Dataset: New Plant Diseases Dataset")
    print(f"Classes: {config.NUM_CLASSES}")
    print(f"Base Model: {config.BASE_MODEL.upper()}")
    print(f"Epochs: {config.EPOCHS}")
    print(f"Batch Size: {config.BATCH_SIZE}")
    print(f"Image Size: {config.IMG_SIZE}")
    print("=" * 70)
    
    # Train model
    model, history, class_names = train_model(config)
    
    # Plot training history
    plot_training_history(history)
    
    # Evaluate model
    _, val_data, _ = create_data_generators(config)
    evaluate_model(model, val_data)
    
    # Optional: Fine-tune for better performance
    # print("\nStarting fine-tuning phase...")
    # model, ft_history = fine_tune_model(model, train_data, val_data, config)
    # evaluate_model(model, val_data)
    
    print("\n" + "=" * 70)
    print("TRAINING COMPLETE!")
    print("=" * 70)
    print(f"[OK] Model saved to: {config.MODEL_SAVE_PATH}")
    print(f"[OK] Ready for export and deployment")
    print("\nClass names:")
    for i, name in enumerate(class_names[:10]):
        print(f"  {i}: {name}")
    if len(class_names) > 10:
        print(f"  ... and {len(class_names) - 10} more classes")
    
    return model, history, class_names


if __name__ == '__main__':
    # Run training
    model, history, class_names = main()