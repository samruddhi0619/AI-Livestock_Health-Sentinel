import os
import cv2
import numpy as np

def validate_image_quality(image_path):
    """
    Validates image file properties and visual quality (resolution, blur, brightness).
    Returns (is_valid, error_message).
    """
    # 1. File Type and Exist check
    if not os.path.exists(image_path):
        return False, "Image file does not exist."
        
    ext = os.path.splitext(image_path)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".bmp"]:
        return False, f"Unsupported image file format: {ext}. Please upload JPG, PNG, or BMP."
        
    # 2. File Size check (limit to 10MB)
    size_mb = os.path.getsize(image_path) / (1024 * 1024)
    if size_mb > 10.0:
        return False, "File size exceeds 10MB limit."
        
    # 3. Read image
    img = cv2.imread(image_path)
    if img is None:
        return False, "Unreadable or corrupted image file."
        
    h, w, c = img.shape
    
    # 4. Resolution Check (min 256x256)
    if h < 256 or w < 256:
        return False, f"Image resolution is too low ({w}x{h}). Minimum required is 256x256 pixels."
        
    # Convert to grayscale for clarity checks
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 5. Brightness check (average intensity)
    mean_brightness = np.mean(gray)
    if mean_brightness < 40.0:
        return False, "Image is too dark. Please upload a well-lit image."
    if mean_brightness > 225.0:
        return False, "Image is too bright / overexposed. Please upload a clearer image."
        
    # 6. Blur Check (Laplacian Variance)
    # A variance below a threshold indicates a lack of high frequency content (edges), meaning it's blurry
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    if lap_var < 50.0:
        return False, "Image is too blurry. Please upload a sharp, clear photo of the animal's symptoms."
        
    return True, "Success"
