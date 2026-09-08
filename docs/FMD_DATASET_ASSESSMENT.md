# Dataset Technical Assessment: Foot-and-Mouth Disease (FMD) Imagery

**Dataset Archive:** `datasets/02_FMD_Cattle_Image_Detection.zip`  
**Processed Directory:** `datasets/processed/02_fmd_detection/`  
**Date of Assessment:** September 2026  
**Document Purpose:** Independent evidence-based audit of data quality, annotation topology, sample sufficiency, and architectural integration.

---

## 1. Executive Summary & Core Determination

Following a comprehensive audit of the archive contents, image metadata, and annotation schemas, the findings are summarized below:

| Audit Criterion | Finding | Clinical / ML Implication |
|---|---|---|
| **Annotation Format** | **COCO Object Detection JSON** (`_annotations.coco.json`) | Contains bounding boxes `[x, y, width, height]`, category IDs, and areas. |
| **Task Type** | **Object Detection** (Localization) | Bounding box spatial localization rather than whole-image classification. |
| **Exact Classes** | Category 0: `cow-4tt4` (0 annotations)<br>Category 1: `foot and mougth` (81 annotations) | Single active target class with a typographical error (`mougth`). Zero negative/healthy controls. |
| **Usable Images** | **80 images total**<br>(Train: 56, Val: 16, Test: 8) | Extremely small sample size. 41 out of 80 images (51.2%) are mobile screenshots. |
| **Training Sufficiency** | **INSUFFICIENT** for statistical deep learning | Far below the minimum threshold ($500 - 1,000+$ instances) required for reliable computer vision. |

### Definitive Strategic Recommendation: **OPTION B — Use Only for Demonstration**

> [!IMPORTANT]
> **Final Recommendation: Option B (Use Only for Demonstration)**  
> - **Do NOT train a production computer vision model** on this dataset. 56 training images without negative controls will cause severe overfitting, feature hallucination, and unacceptable false-positive rates on farm imagery.
> - **Use strictly for UI/UX demonstration** in the **Veterinarian Case Review Portal** (Feature 9 & Feature 14) to illustrate how veterinary bounding box overlays and lesion annotations appear in clinical triage queues.
> - **FMD clinical diagnosis in AI-Livestock Health Sentinel remains firmly powered by the tabular symptom and vitals models** (trained on 9,701 FMD cases from Dataset 05 and 2,593 FMD cases with vaccination histories from Dataset 06), where empirical statistical power is verified.

---

## 2. Detailed Technical Audit Findings

### Question 1: What Annotation Format Does It Use?
The dataset uses the standard **Microsoft COCO (Common Objects in Context) JSON format**:
- Files: `train/_annotations.coco.json`, `valid/_annotations.coco.json`, `test/_annotations.coco.json`
- Each JSON file contains five top-level keys:
  1. `info`: Exported via Roboflow (March 12, 2025).
  2. `licenses`: Creative Commons Attribution 4.0 (`CC BY 4.0`).
  3. `categories`: Defines category names and numerical IDs.
  4. `images`: Image manifests (`id`, `file_name`, `width`, `height`).
  5. `annotations`: Spatial labels (`id`, `image_id`, `category_id`, `bbox`, `area`, `segmentation: []`, `iscrowd: 0`).
- Bounding Box Format: Standard COCO pixel coordinates:
  $$\text{bbox} = [x_{\text{min}}, y_{\text{min}}, \text{width}, \text{height}]$$
  *Example:* `[3, 27, 168.39, 215.22]`, `area: 36240.896`

### Question 2: Is It Classification or Object Detection?
- **It is strictly an Object Detection dataset.**
- While the Roboflow project slug contains the text `image-classification-chkt8`, the actual dataset exported and annotated consists of **2D bounding boxes localized around specific oral and digital lesions**.
- It is **not** an image classification dataset; images are not categorized at the image level into distinct disease folders, but rather tagged with spatial bounding boxes demarcating suspicious tissue.

### Question 3: What Are the Exact Classes?
The dataset defines two category entities in the COCO header:
1. `id: 0`, `name: "cow-4tt4"`, `supercategory: "none"`
2. `id: 1`, `name: "foot and mougth"`, `supercategory: "cow-4tt4"`

#### Class Distribution Analysis
| Category ID | Name in Header | Instances in `train` | Instances in `valid` | Instances in `test` | Total Annotations |
|:---:|---|:---:|:---:|:---:|:---:|
| **0** | `cow-4tt4` | 0 | 0 | 0 | **0** |
| **1** | `foot and mougth` | 57 | 16 | 8 | **81** |

**Critical Observation:**
- **Zero negative controls exist:** There are **no healthy cattle hooves, healthy mouths, or negative control images** anywhere in the dataset.
- Category 0 is an empty placeholder with 0 annotations.
- 100% of the active annotations (81 boxes across 80 images) belong to Category 1 (`foot and mougth`).

### Question 4: Number of Usable Images
The dataset contains **80 images in total**:
- `train/`: 56 images (57 bounding boxes)
- `valid/`: 16 images (16 bounding boxes)
- `test/`: 8 images (8 bounding boxes)

#### Image Quality & Origin Audit
- **Screenshot Artifacts:** 41 out of 80 images (**51.2%**) are mobile phone screen captures with filenames like `Screenshot__-_-_-_-_-_-_-_-_-_-_-_-_-_-_png.rf...jpg` at dimensions $720 \times 1600$ or $1600 \times 720$ pixels.
- **Resolution Heterogeneity:** Resolutions vary drastically from $171 \times 296$ pixels up to $1600 \times 1600$ pixels (mean: $772 \times 947$ px).
- **Bounding Box Sizing Anomaly:** The average bounding box occupies **46.6% of the total image area** in the training set (with maximum bounding box covering **98.4%** of the image). In many screenshots, annotators drew a single box encompassing the entire smartphone screen rather than precisely delineating localized vesicles or ulcers.

### Question 5: Is the Dataset Large Enough for Reliable Training?
**No. The dataset is orders of magnitude below the threshold for reliable training.**

```
                        TRAINING SAMPLE SIZE COMPARISON
 ┌────────────────────────────────────────────────────────────────────────┐
 │ Typical Minimum for Transfer Learning Object Detection (YOLO/COCO)     │
 │ ██████████████████████████████████████████████████ 500 - 1,000+ images │
 ├────────────────────────────────────────────────────────────────────────┤
 │ Available FMD Training Split                                           │
 │ █ 56 images (57 bounding boxes)                                        │
 └────────────────────────────────────────────────────────────────────────┘
```

#### Why 56 Training Images Is Scientifically Inadequate:
1. **Severe Overfitting:** Modern single-stage object detectors (such as YOLOv8n with 3.2M parameters or Faster R-CNN with 41M parameters) will memorize individual phone screenshots rather than generalizable pathological biomarkers.
2. **Lack of Negative Controls:** Without images of healthy bovine muzzles, normal interdigital spaces, or differential diagnoses (e.g., Bovine Viral Diarrhea erosions, Vesicular Stomatitis, foot rot), an object detector trained on this data would fire false-positive detections on almost any bovine foot or snout presented to it.
3. **Statistical Insignificance of the Test Split:** With only 8 images in the test set, a single misclassified image swings the evaluation metric by **12.5%**, rendering mAP (mean Average Precision) and recall figures statistically meaningless.

---

## 3. Comparison of Options A, B, and C

| Option | Feasibility | Scientific Validity | Clinical Safety Risk | Evaluation Verdict |
|---|:---:|:---:|:---:|---|
| **A. Build a secondary experimental FMD model** | Low | Very Low | **High:** Risk of false reassurance or false alarms for a high-consequence Category-A transboundary disease. | **REJECTED:** Training a deep detector on 56 images creates an illusion of capability that fails in field conditions. |
| **B. Use only for demonstration** | **High** | **High** | **Low:** Transparently showcased as UI mockup data without automated diagnostic claims. | **RECOMMENDED:** Displays realistic lesion bounding boxes in the Veterinarian Review Portal while relying on tabular ML for diagnosis. |
| **C. Exclude from final ML pipeline completely** | **High** | **High** | **Zero:** Completely eliminates computer vision false positives for FMD. | **ACCEPTED IN PART:** FMD imagery is excluded from autonomous computer vision inference; retained solely for UI demonstration. |

---

## 4. Final System Architecture Integration

To balance engineering realism with product requirements for the Smart India Hackathon:

```
                                FMD SURVEILLANCE PIPELINE
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. CLINICAL DIAGNOSTIC CORE (Production Machine Learning)                              │
│    • Dataset 05: animal_disease_dataset.csv (9,701 confirmed FMD cases)                │
│    • Dataset 06: global_cattle_disease_detection_dataset.csv (2,593 FMD cases)         │
│    • ML Models: Random Forest / Gradient Boosting with multi-hot symptom vectorization │
│    • Features: Blisters on hooves, sores on tongue, lameness, salivation, FMD vaccine  │
│    • Status: 100% OPERATIONAL & STATISTICALLY RIGOROUS (Accuracy: 90.8%)               │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
┌───────────────────────────────────────────┴────────────────────────────────────────────┐
│ 2. VETERINARIAN CASE REVIEW PORTAL (UI / Demonstration Layer)                          │
│    • Uses the 80 FMD COCO annotations to demonstrate interactive lesion bounding boxes │
│    • Allows veterinarians to inspect uploaded case reports with visual overlay         │
│    • Explicitly marked: "Demo Case Asset - Manual Clinical Triage Required"            │
│    • Status: EMBEDDED IN VET PORTAL WITHOUT UNVALIDATED AUTONOMOUS INFERENCE           │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **No Autonomous Vision Inference for FMD:**
   The primary computer vision inference pipeline ([`predict_image.py`](file:///C:/Users/Samruddhi%20Janwalkar/.gemini/antigravity/scratch/ai-livestock-health-sentinel/ml/image_lsd/predict_image.py)) remains dedicated to **Lumpy Skin Disease**, where 935 high-quality whole-cow images provide sufficient statistical support (86.5% accuracy, 92.3% precision).
2. **FMD Handled via Clinical Symptoms & Vitals:**
   Foot-and-Mouth Disease is accurately screened through the symptom-based assessment engine, which leverages oral blister patterns, salivation, lameness, and FMD vaccination history.
3. **UI Demonstration Asset:**
   The 80 FMD images and their sanitized COCO annotations in `datasets/processed/02_fmd_detection/` will be used exclusively to demonstrate interactive bounding box overlays in the Veterinarian Dashboard.

---

## 5. Regulatory & Clinical Safety Note

> [!CAUTION]
> **Foot-and-Mouth Disease (FMD) is a Tier-1 Transboundary Notifiable Disease** under the World Organisation for Animal Health (WOAH / OIE) and the Department of Animal Husbandry and Dairying (DAHD), Government of India.  
> Attempting to automate regulatory quarantine or disease clearance using an unverified 56-image computer vision model would pose biosecurity and regulatory risks. FMD detection in this platform is grounded strictly in veterinary-reported clinical symptoms, epidemiological contact tracing, and spatial cluster detection.
