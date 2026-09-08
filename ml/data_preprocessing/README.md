# Data Preprocessing Pipelines (`ml/data_preprocessing/`)

This directory contains standalone, reproducible preprocessing pipelines for each of the 7 project datasets.

## Pipeline Scripts

| Pipeline Script | Target Dataset | Core Operations |
|---|---|---|
| `preprocess_01_lsd_images.py` | `01_LSD_vs_Healthy_Cattle_Images.zip` | Palette-to-RGB normalization, Lanczos resize to 224×224, stratified 70/15/15 split, training-only photometric/rotational augmentation. |
| `preprocess_02_fmd_detection.py` | `02_FMD_Cattle_Image_Detection.zip` | COCO bounding box integrity validation, resolution sanitization, split verification (`train`, `val`, `test`). |
| `preprocess_03_environmental.py` | `03_LSD_Environmental_Geospatial_Data.zip` | **Target leakage elimination** (drops `region`, `country`, `reportingDate`), one-hot encodes land cover, stratified 70/15/15 split, fits StandardScaler on train split only. |
| `preprocess_04_skin_images.py` | `04_LSD_vs_Normal_Skin_Images.zip` | RGBA-to-RGB conversion, standardized 256×256 square crops, stratified 70/15/15 split, training-only dermatological orientation augmentation. |
| `preprocess_05_symptoms.py` | `05_Cattle_Health_Feeding_Records.zip` | Fahrenheit-to-Celsius conversion ($T_C = (T_F - 32) \times 5/9$), permutation-invariant multi-hot symptom encoding, stratified 70/15/15 split. |
| `preprocess_06_disease_telemetry.py` | `06_Cattle_Disease_and_Health_Records.zip` | Drops pure ID/date memorization tokens, encodes 40 breeds and 45 diseases, stratified split, fits continuous vitals scaler on train only, exports healthy vitals baseline for Isolation Forest. |
| `preprocess_07_symptom_dictionary.py` | `07_Animal_Symptoms_Disease_Prediction.zip` | Deduplicates rows, sanitizes corrupted temperature strings, extracts standardized bovine symptom ontology. |

## Quick Execution

Run all pipelines in sequence:
```bash
python ml/data_preprocessing/run_all_preprocessing.py
```

Or run any pipeline individually:
```bash
python ml/data_preprocessing/preprocess_03_environmental.py
```

Processed datasets and metadata are stored separately in `datasets/processed/` without altering original archives.
