import os
import zipfile
import json
import random
import pandas as pd
import numpy as np
from PIL import Image, ImageEnhance, ImageOps

from base_preprocessor import compute_md5, ensure_dir, safe_load_image, stratified_split_indices

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ZIP_PATH = os.path.join(ROOT_DIR, "datasets", "01_LSD_vs_Healthy_Cattle_Images.zip")
OUTPUT_DIR = os.path.join(ROOT_DIR, "datasets", "processed", "01_lsd_images")

TARGET_SIZE = (224, 224)
RANDOM_SEED = 42

def apply_training_augmentation(img: Image.Image, seed: int) -> Image.Image:
    """
    Applies photometric and geometric augmentations ONLY for training images.
    Validation and testing sets are strictly preserved without artificial alterations.
    """
    rng = random.Random(seed)
    
    # 1. Random Horizontal Flip (50% probability)
    if rng.random() > 0.5:
        img = ImageOps.mirror(img)
        
    # 2. Random slight rotation (-10 to +10 degrees)
    angle = rng.uniform(-10, 10)
    img = img.rotate(angle, resample=Image.BICUBIC, fillcolor=(128, 128, 128))
    
    # 3. Random Color Jitter (Brightness: 0.85 - 1.15)
    enh_bright = ImageEnhance.Brightness(img)
    img = enh_bright.enhance(rng.uniform(0.85, 1.15))
    
    # 4. Random Contrast (0.85 - 1.15)
    enh_contrast = ImageEnhance.Contrast(img)
    img = enh_contrast.enhance(rng.uniform(0.85, 1.15))
    
    return img

def process_dataset_01():
    print("==========================================================")
    print("PREPROCESSING DATASET 01: LSD vs Healthy Cattle Images")
    print("==========================================================")
    
    if not os.path.exists(ZIP_PATH):
        raise FileNotFoundError(f"Source archive not found: {ZIP_PATH}")
        
    ensure_dir(OUTPUT_DIR)
    
    records = []
    seen_hashes = set()
    corrupted_count = 0
    duplicate_count = 0
    
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        file_list = [f for f in z.namelist() if not f.endswith('/') and any(f.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png'])]
        print(f"Found {len(file_list)} raw candidate images.")
        
        for f in file_list:
            parts = f.split('/')
            label = parts[0] if len(parts) > 1 else "unknown"
            filename = os.path.basename(f)
            
            raw_bytes = z.read(f)
            md5_hash = compute_md5(raw_bytes)
            
            if md5_hash in seen_hashes:
                duplicate_count += 1
                continue
            seen_hashes.add(md5_hash)
            
            img = safe_load_image(raw_bytes)
            if img is None:
                corrupted_count += 1
                continue
                
            orig_w, orig_h = img.size
            
            records.append({
                "source_path": f,
                "filename": filename,
                "label": label,
                "orig_w": orig_w,
                "orig_h": orig_h,
                "md5": md5_hash
            })
            
    df = pd.DataFrame(records)
    print(f"Clean valid unique images: {len(df)} (Corrupted: {corrupted_count}, Duplicates removed: {duplicate_count})")
    print(f"Class distribution:\n{df['label'].value_counts().to_dict()}")
    
    # Stratified Train/Val/Test Split (70% / 15% / 15%)
    labels = df['label'].values
    train_idx, val_idx, test_idx = stratified_split_indices(labels, 0.70, 0.15, 0.15, RANDOM_SEED)
    
    df['split'] = 'train'
    df.loc[val_idx, 'split'] = 'val'
    df.loc[test_idx, 'split'] = 'test'
    
    # Save normalized images by split and class
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        for idx, row in df.iterrows():
            raw_bytes = z.read(row['source_path'])
            img = safe_load_image(raw_bytes)
            
            # High-quality Lanczos resize to 224x224
            img_resized = img.resize(TARGET_SIZE, Image.LANCZOS)
            
            # Apply augmentation only to train split
            if row['split'] == 'train':
                img_final = apply_training_augmentation(img_resized, seed=idx)
            else:
                img_final = img_resized # Strictly unaugmented
                
            out_folder = os.path.join(OUTPUT_DIR, row['split'], row['label'])
            ensure_dir(out_folder)
            out_path = os.path.join(out_folder, row['filename'])
            img_final.save(out_path, format="JPEG", quality=95)
            
    # Export split metadata
    meta_path = os.path.join(OUTPUT_DIR, "metadata.csv")
    df.to_csv(meta_path, index=False)
    
    summary = {
        "dataset_name": "01_LSD_vs_Healthy_Cattle_Images",
        "total_processed": len(df),
        "target_resolution": list(TARGET_SIZE),
        "train_samples": len(train_idx),
        "val_samples": len(val_idx),
        "test_samples": len(test_idx),
        "class_breakdown": df['label'].value_counts().to_dict(),
        "train_augmented": True,
        "val_test_augmented": False
    }
    with open(os.path.join(OUTPUT_DIR, "summary.json"), "w") as jf:
        json.dump(summary, jf, indent=2)
        
    print(f"[SUCCESS] Dataset 01 processed. Saved to {OUTPUT_DIR}")
    print(f"Summary: {summary}")

if __name__ == "__main__":
    process_dataset_01()
