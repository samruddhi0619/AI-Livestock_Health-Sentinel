# Image-Based Lumpy Skin Disease (LSD) Visual Screening (`ml/image_lsd`)

This module provides visual screening and hide lesion analysis for cattle suspected of Lumpy Skin Disease (LSD) or cutaneous ulcerations.

## Architecture

1. **Pre-Screening Quality Validation (`image_quality.py`)**:
   - Validates file format (`.jpg`, `.jpeg`, `.png`, `.bmp`) and size ($\le 10$ MB).
   - Validates spatial resolution (minimum $256 \times 256$ pixels).
   - Checks mean illumination intensity (bounds: 40 to 225) to reject under/over-exposed photos.
   - Computes Laplacian blur variance ($\text{Var} \ge 50.0$) to reject out-of-focus or motion-blurred inputs.

2. **Computer Vision Lesion Analysis (`predict_image.py`)**:
   - Converts RGB imagery to HSV color space.
   - Segments circumscribed nodular erythema and dark scabbed necrotic tissue.
   - Applies elliptical morphological opening/closing operations to filter hair texture noise.
   - Identifies contour boundaries, computes lesion counts, and measures lesion surface area ratio.
   - Generates an `abnormality_score` ($0.0 - 100.0$) and descriptive clinical findings.

3. **PyTorch MobileNet Integration Point**:
   - Ready for fine-tuned MobileNetV3 deep feature extraction transfer learning checkpoint.
