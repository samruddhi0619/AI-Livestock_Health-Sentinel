# Datasets Directory (`datasets/`)

This directory contains reference dataset schemas, generation scripts, and sample training vectors for livestock disease modeling.

## Contents
- `generate_dataset.py`: Reproducible synthetic generator simulating clinical distributions for 6 cattle conditions based on veterinary epidemiology literature (ICAR / DAHD).
- `sample_cattle_symptoms.csv`: A 100-row demonstration sample showing the structure of input demographic and clinical symptoms.

## Git & Large File Guidelines
- **Git LFS**: Large training datasets (e.g., thousands of high-resolution cattle hide photos or multi-gigabyte tabular logs) must NOT be committed directly to Git. Use Git LFS (`git lfs track "*.csv"` or store in cloud object storage like S3/GCS).
- Files in `datasets/raw/` and `datasets/processed/` are automatically excluded via `.gitignore`.
