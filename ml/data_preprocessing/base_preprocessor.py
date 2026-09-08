import os
import sys
import hashlib
import json
import numpy as np
from PIL import Image

def compute_md5(data: bytes) -> str:
    """Computes MD5 hash for image/data deduplication."""
    return hashlib.md5(data).hexdigest()

def ensure_dir(path: str):
    """Recursively creates directory if it does not exist."""
    os.makedirs(path, exist_ok=True)

def safe_load_image(img_bytes: bytes):
    """
    Safely opens an image from bytes, validates its integrity,
    and returns an RGB PIL Image or None if corrupted.
    """
    import io
    try:
        img = Image.open(io.BytesIO(img_bytes))
        img.verify() # Verify file integrity
        # Re-open after verify() because verify changes pointer
        img = Image.open(io.BytesIO(img_bytes))
        # Standardize color space: convert Palette (P), Grayscale (L), RGBA to RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        return img
    except Exception:
        return None

def stratified_split_indices(labels, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, random_seed=42):
    """
    Computes stratified train, validation, and test indices for a given array of class labels.
    Guarantees no data leakage across splits.
    """
    from sklearn.model_selection import train_test_split
    
    indices = np.arange(len(labels))
    test_size = val_ratio + test_ratio
    
    train_idx, temp_idx, y_train, y_temp = train_test_split(
        indices, labels,
        test_size=test_size,
        stratify=labels,
        random_state=random_seed
    )
    
    # Relative ratio for val and test
    relative_val_size = val_ratio / test_size
    val_idx, test_idx = train_test_split(
        temp_idx,
        test_size=(1.0 - relative_val_size),
        stratify=y_temp,
        random_state=random_seed
    )
    
    return train_idx, val_idx, test_idx
