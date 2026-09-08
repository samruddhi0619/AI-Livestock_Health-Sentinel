import os
import zipfile
import json
import random
import pandas as pd
import numpy as np
from PIL import Image, ImageEnhance, ImageOps

from base_preprocessor import compute_md5, ensure_dir, safe_load_image, stratified_split_indices

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ZIP_PATH = os.path.join(ROOT_DIR, "datasets", "04_LSD_vs_Normal_Skin_Images.zip")
OUTPUT_DIR = os.path.join(ROOT_DIR, "datasets", "processed", "04_skin_images")

TARGET_SIZE = (256, 256) # Standard square dermatological patch size
RANDOM_SEED = 42

def apply_skin_training_augmentation(img: Image.Image, seed: int) -> Image.Image:
    """
    Photometric and rotational augmentation strictly for training skin patches.
    Leaves validation and test sets untouched.
    """
    rng = random.Random(seed)
    
    # 1. Random Horizontal & Vertical Flips (Dermatological patches are orientation invariant)
    if rng.random() > 0.5:
        img = ImageOps.mirror(img)
    if rng.random() > 0.5:
        img = ImageOps.flip(img)
        
    # 2. Random 90 degree or subtle rotation
    angle = rng.choice([0, 90, 180, 270]) + rng.uniform(-5, 5)
    img = img.rotate(angle, resample=Image.BICUBIC)
    
    # 3. Random Brightness (0.9 - 1.1)
    enh_bright = ImageEnhance.Brightness(img)
    img = enh_bright.enhance(rng.uniform(0.9, 1.1))
    
    # 4. Random Contrast (0.9 - 1.1)
    enh_contrast = ImageEnhance.Contrast(img)
    img = enh_contrast.enhance(rng.uniform(0.9, 1.1))
    
    return img

def process_dataset_04():
    print("==========================================================")
    print("PREPROCESSING DATASET 04: LSD vs Normal Skin Images")
    print("==========================================================")
    
    if not os.path.exists(ZIP_PATH):
        raise FileNotFoundError(f"Source archive not found: {ZIP_PATH}")
        
    ensure_dir(OUTPUT_DIR)
    
    records = []
    seen_hashes = set()
    corrupted_count = 0
    duplicate_count = 0
    rgba_converted_count = 0
    
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        file_list = [f for f in z.namelist() if not f.endswith('/') and f.lower().endswith('.png')]
        print(f"Found {len(file_list)} raw skin patch images.")
        
        for f in file_list:
            parts = f.split('/')
            label_raw = parts[0] if len(parts) > 1 else "unknown"
            # Normalize label name: 'Normal_Skin' or 'Lumpy_Skin'
            label = label_raw.replace(' ', '_')
            filename = os.path.basename(f)
            
            raw_bytes = z.read(f)
            md5_hash = compute_md5(raw_bytes)
            
            if md5_hash in seen_hashes:
                duplicate_count += 1
                continue
            seen_hashes.add(md5_hash)
            
            # Safe load handles RGBA -> RGB strip
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
    print(f"Valid unique images: {len(df)} (Corrupted: {corrupted_count}, Duplicates removed: {duplicate_count})")
    print(f"Class distribution:\n{df['label'].value_counts().to_dict()}")
    
    # Stratified Train/Val/Test Split (70% / 15% / 15%)
    labels = df['label'].values
    train_idx, val_idx, test_idx = stratified_split_indices(labels, 0.70, 0.15, 0.15, RANDOM_SEED)
    
    df['split'] = 'train'
    df.loc[val_idx, 'split'] = 'val'
    df.loc[test_idx, 'split'] = 'test'
    
    # Save normalized images
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        for idx, row in df.iterrows():
            raw_bytes = z.read(row['source_path'])
            img = safe_load_image(raw_bytes)
            
            img_resized = img.resize(TARGET_SIZE, Image.LANCZOS)
            
            if row['split'] == 'train':
                img_final = apply_skin_training_augmentation(img_resized, seed=idx)
            else:
                img_final = img_resized
                
            out_folder = os.path.join(OUTPUT_DIR, row['split'], row['label'])
            ensure_dir(out_folder)
            out_path = os.path.join(out_folder, row['filename'])
            img_final.save(out_path, format="PNG")
            
    meta_path = os.path.join(OUTPUT_DIR, "metadata.csv")
    df.to_csv(meta_path, index=False)
    
    summary = {
        "dataset_name": "04_LSD_vs_Normal_Skin_Images",
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
        
    print(f"[SUCCESS] Dataset 04 processed. Saved to {OUTPUT_DIR}")
    print(f"Summary: {summary}")

if __name__ == "__main__":
    process_dataset_04()
