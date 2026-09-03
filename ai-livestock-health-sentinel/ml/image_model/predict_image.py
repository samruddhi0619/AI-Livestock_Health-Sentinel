import cv2
import numpy as np
from image_quality import validate_image_quality

def analyze_animal_image(image_path):
    """
    Performs Computer Vision skin lesion detection using HSV thresholding and contour analysis.
    Returns a dictionary of results including abnormality presence, lesion count, and score.
    """
    # 1. Quality validation
    is_valid, msg = validate_image_quality(image_path)
    if not is_valid:
        return {
            "abnormality_detected": False,
            "error": msg,
            "lesion_count": 0,
            "abnormality_score": 0.0,
            "visual_findings": "Quality check failed: " + msg
        }
        
    # 2. Read image
    img = cv2.imread(image_path)
    h, w, _ = img.shape
    total_pixels = h * w
    
    # 3. Convert to HSV color space for color segmentation
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Segment reddish/pinkish inflamed skin lesions or sores
    # Lower red range
    lower_red1 = np.array([0, 40, 40])
    upper_red1 = np.array([12, 255, 255])
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    
    # Upper red range
    lower_red2 = np.array([168, 40, 40])
    upper_red2 = np.array([180, 255, 255])
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    
    # Segment dark scabbed/crusty lesion nodes
    lower_dark = np.array([0, 0, 0])
    upper_dark = np.array([180, 80, 45])
    mask_dark = cv2.inRange(hsv, lower_dark, upper_dark)
    
    # Combine masks
    mask = mask_red1 | mask_red2 | mask_dark
    
    # 4. Cleanup noise using morphological operations (Opening to remove small dots, Closing to group clusters)
    kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    
    cleaned = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_open)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel_close)
    
    # 5. Extract lesion structures (Contours)
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    lesion_count = 0
    total_lesion_area = 0
    
    # Filter contours based on minimum area (e.g., 200 pixels) to avoid small artifacts
    min_contour_area = 200
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > min_contour_area:
            lesion_count += 1
            total_lesion_area += area
            
    coverage_ratio = total_lesion_area / total_pixels
    
    # Abnormality scoring logic based on coverage and lesion count
    # Max out at 100
    abnormality_score = min(100.0, (coverage_ratio * 400.0) + (lesion_count * 8.0))
    
    abnormality_detected = (lesion_count >= 2 and abnormality_score > 15.0) or (abnormality_score > 30.0)
    
    # Build findings description
    if abnormality_detected:
        if lesion_count > 6:
            visual_findings = f"Multiple circular skin abnormalities ({lesion_count} nodules/scabs) detected, covering {coverage_ratio*100:.1f}% of inspected area. Consistent with cutaneous lesions."
        else:
            visual_findings = f"Skin irregularities / localized sores ({lesion_count} spots) detected, covering {coverage_ratio*100:.1f}% of inspected area."
    else:
        visual_findings = "No significant skin lesions or visible abnormalities detected on the animal's hide."
        
    return {
        "abnormality_detected": bool(abnormality_detected),
        "lesion_count": int(lesion_count),
        "abnormality_score": round(float(abnormality_score), 1),
        "visual_findings": visual_findings
    }
