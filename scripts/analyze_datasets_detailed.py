import os
import zipfile
import io
import json
import hashlib
from collections import Counter
import pandas as pd
import numpy as np

DATASETS_DIR = r"C:\Users\Samruddhi Janwalkar\.gemini\antigravity\scratch\ai-livestock-health-sentinel\datasets"

def inspect_image_zip(zip_name):
    print(f"\n{'='*70}\nINSPECTING IMAGE ZIP: {zip_name}\n{'='*70}")
    zip_path = os.path.join(DATASETS_DIR, zip_name)
    with zipfile.ZipFile(zip_path, 'r') as z:
        namelist = z.namelist()
        files = [n for n in namelist if not n.endswith('/')]
        print(f"Total files: {len(files)}")
        
        # Check subfolders
        folder_counts = Counter()
        ext_counts = Counter()
        md5_hashes = set()
        duplicate_images = 0
        
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            ext_counts[ext] += 1
            parts = f.split('/')
            if len(parts) > 1:
                folder_counts[parts[0]] += 1
            else:
                folder_counts["[root]"] += 1
                
            # Check duplicate hashes for image files
            if ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                data = z.read(f)
                h = hashlib.md5(data).hexdigest()
                if h in md5_hashes:
                    duplicate_images += 1
                else:
                    md5_hashes.add(h)
                    
        print(f"File extensions: {dict(ext_counts)}")
        print(f"Folder/Class distribution: {dict(folder_counts)}")
        print(f"Unique image hashes: {len(md5_hashes)}, Duplicate images by content: {duplicate_images} ({(duplicate_images/max(1, len(files)))*100:.2f}%)")
        
        # If roboflow / coco annotations exist
        coco_files = [f for f in files if f.endswith('.json')]
        if coco_files:
            print(f"Annotation files found: {coco_files}")
            for cf in coco_files:
                try:
                    ann_data = json.loads(z.read(cf).decode('utf-8'))
                    cats = ann_data.get('categories', [])
                    images = ann_data.get('images', [])
                    annotations = ann_data.get('annotations', [])
                    print(f"  {cf}: {len(images)} images, {len(annotations)} annotations, Categories: {cats}")
                except Exception as e:
                    print(f"  Error reading {cf}: {e}")

def inspect_tabular_zip(zip_name):
    print(f"\n{'='*70}\nINSPECTING TABULAR ZIP: {zip_name}\n{'='*70}")
    zip_path = os.path.join(DATASETS_DIR, zip_name)
    with zipfile.ZipFile(zip_path, 'r') as z:
        csv_files = [n for n in z.namelist() if n.endswith('.csv')]
        for csv_f in csv_files:
            print(f"\n--- CSV File: {csv_f} ---")
            with z.open(csv_f) as f:
                df = pd.read_csv(f)
            print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
            print(f"Columns: {list(df.columns)}")
            
            # Duplicates
            dup_count = df.duplicated().sum()
            print(f"Duplicate Rows: {dup_count} ({(dup_count/len(df))*100:.2f}%)")
            
            # Nulls
            null_cols = {col: df[col].isnull().sum() for col in df.columns if df[col].isnull().sum() > 0}
            print(f"Missing Values: {null_cols if null_cols else 'None (0 nulls across all columns)'}")
            
            # Data Types
            print("\nColumn Summary:")
            for col in df.columns:
                n_unique = df[col].nunique()
                dtype = str(df[col].dtype)
                sample = df[col].dropna().unique()[:3].tolist()
                print(f"  {col} [{dtype}]: {n_unique} unique values. Sample: {sample}")
                
            # Class Distributions (columns with <= 20 unique values)
            print("\nCategorical Distributions (<= 20 unique values):")
            for col in df.columns:
                if df[col].nunique() <= 20:
                    counts = df[col].value_counts(dropna=False).to_dict()
                    print(f"  {col}: {counts}")

if __name__ == "__main__":
    # Image datasets
    inspect_image_zip('01_LSD_vs_Healthy_Cattle_Images.zip')
    inspect_image_zip('02_FMD_Cattle_Image_Detection.zip')
    inspect_image_zip('04_LSD_vs_Normal_Skin_Images.zip')
    
    # Tabular datasets
    inspect_tabular_zip('03_LSD_Environmental_Geospatial_Data.zip')
    inspect_tabular_zip('05_Cattle_Health_Feeding_Records.zip')
    inspect_tabular_zip('06_Cattle_Disease_and_Health_Records.zip')
    inspect_tabular_zip('07_Animal_Symptoms_Disease_Prediction.zip')
