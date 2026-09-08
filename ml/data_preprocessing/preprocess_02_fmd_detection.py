import os
import zipfile
import json
import pandas as pd
from PIL import Image

from base_preprocessor import compute_md5, ensure_dir, safe_load_image

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ZIP_PATH = os.path.join(ROOT_DIR, "datasets", "02_FMD_Cattle_Image_Detection.zip")
OUTPUT_DIR = os.path.join(ROOT_DIR, "datasets", "processed", "02_fmd_detection")

def process_dataset_02():
    print("==========================================================")
    print("PREPROCESSING DATASET 02: FMD Cattle Image Detection")
    print("==========================================================")
    
    if not os.path.exists(ZIP_PATH):
        raise FileNotFoundError(f"Source archive not found: {ZIP_PATH}")
        
    ensure_dir(OUTPUT_DIR)
    
    split_summaries = {}
    total_valid_images = 0
    total_valid_annotations = 0
    
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        for split in ['train', 'valid', 'test']:
            dest_split = 'val' if split == 'valid' else split
            split_out_dir = os.path.join(OUTPUT_DIR, dest_split)
            ensure_dir(split_out_dir)
            
            coco_file = f"{split}/_annotations.coco.json"
            if coco_file not in z.namelist():
                continue
                
            coco_data = json.loads(z.read(coco_file).decode('utf-8'))
            images_meta = coco_data.get('images', [])
            annotations = coco_data.get('annotations', [])
            categories = coco_data.get('categories', [])
            
            valid_images = []
            valid_image_ids = set()
            
            # 1. Validate images and save to processed directory
            for img_info in images_meta:
                img_path = f"{split}/{img_info['file_name']}"
                if img_path not in z.namelist():
                    continue
                    
                raw_bytes = z.read(img_path)
                img = safe_load_image(raw_bytes)
                if img is None:
                    continue # Corrupted
                    
                out_img_path = os.path.join(split_out_dir, img_info['file_name'])
                img.save(out_img_path, format="JPEG", quality=95)
                
                valid_images.append(img_info)
                valid_image_ids.add(img_info['id'])
                
            # 2. Filter and validate annotations matching valid images
            cleaned_annotations = []
            for ann in annotations:
                if ann['image_id'] in valid_image_ids:
                    # Bounding box bounds check [x, y, w, h]
                    x, y, w, h = ann['bbox']
                    if w > 0 and h > 0:
                        cleaned_annotations.append(ann)
                        
            # 3. Export sanitized split COCO JSON
            sanitized_coco = {
                "info": coco_data.get("info", {"description": "FMD Lesion Object Detection"}),
                "categories": categories,
                "images": valid_images,
                "annotations": cleaned_annotations
            }
            
            out_coco_path = os.path.join(split_out_dir, "_annotations.coco.json")
            with open(out_coco_path, "w") as jf:
                json.dump(sanitized_coco, jf, indent=2)
                
            split_summaries[dest_split] = {
                "image_count": len(valid_images),
                "annotation_count": len(cleaned_annotations)
            }
            total_valid_images += len(valid_images)
            total_valid_annotations += len(cleaned_annotations)
            
    summary = {
        "dataset_name": "02_FMD_Cattle_Image_Detection",
        "total_images": total_valid_images,
        "total_annotations": total_valid_annotations,
        "splits": split_summaries,
        "categories": categories,
        "output_format": "COCO Object Detection"
    }
    
    with open(os.path.join(OUTPUT_DIR, "summary.json"), "w") as jf:
        json.dump(summary, jf, indent=2)
        
    print(f"[SUCCESS] Dataset 02 processed. Saved to {OUTPUT_DIR}")
    print(f"Summary: {summary}")

if __name__ == "__main__":
    process_dataset_02()
