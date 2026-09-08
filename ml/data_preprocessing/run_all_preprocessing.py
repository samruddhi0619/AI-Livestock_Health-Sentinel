import os
import sys
import time
import json

# Add current directory to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)

from preprocess_01_lsd_images import process_dataset_01
from preprocess_02_fmd_detection import process_dataset_02
from preprocess_03_environmental import process_dataset_03
from preprocess_04_skin_images import process_dataset_04
from preprocess_05_symptoms import process_dataset_05
from preprocess_06_disease_telemetry import process_dataset_06
from preprocess_07_symptom_dictionary import process_dataset_07

def main():
    start_total = time.time()
    print("==================================================================")
    print("STARTING REPRODUCIBLE PREPROCESSING FOR ALL 7 LIVESTOCK DATASETS")
    print("==================================================================")
    
    pipelines = [
        ("01_LSD_vs_Healthy_Cattle_Images", process_dataset_01),
        ("02_FMD_Cattle_Image_Detection", process_dataset_02),
        ("03_LSD_Environmental_Geospatial_Data", process_dataset_03),
        ("04_LSD_vs_Normal_Skin_Images", process_dataset_04),
        ("05_Cattle_Health_Feeding_Records", process_dataset_05),
        ("06_Cattle_Disease_and_Health_Records", process_dataset_06),
        ("07_Animal_Symptoms_Disease_Prediction", process_dataset_07),
    ]
    
    report = []
    
    for name, func in pipelines:
        t0 = time.time()
        print(f"\n>>> Executing Pipeline: {name} ...")
        try:
            func()
            elapsed = time.time() - t0
            report.append({
                "dataset": name,
                "status": "SUCCESS",
                "elapsed_seconds": round(elapsed, 2)
            })
            print(f">>> [SUCCESS] {name} completed in {elapsed:.2f} seconds.")
        except Exception as e:
            elapsed = time.time() - t0
            report.append({
                "dataset": name,
                "status": "FAILED",
                "error": str(e),
                "elapsed_seconds": round(elapsed, 2)
            })
            print(f">>> [ERROR] {name} failed: {e}")
            
    total_elapsed = time.time() - start_total
    print("\n==================================================================")
    print("PREPROCESSING PIPELINE EXECUTION REPORT")
    print("==================================================================")
    for item in report:
        print(f" - {item['dataset']}: {item['status']} ({item['elapsed_seconds']}s)")
    print(f"\nTotal execution time: {total_elapsed:.2f} seconds.")
    print("==================================================================")

if __name__ == "__main__":
    main()
