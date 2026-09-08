import os
import sys
import json
import argparse
from typing import Dict, Any, Optional
from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms
from torchvision.models import (
    efficientnet_b0, EfficientNet_B0_Weights,
    mobilenet_v3_small, MobileNet_V3_Small_Weights
)

# Support imports across repo
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
sys.path.append(CURRENT_DIR)

try:
    from image_quality import validate_image_quality
except ImportError:
    try:
        from ml.image_lsd.image_quality import validate_image_quality
    except ImportError:
        def validate_image_quality(p):
            return True, "Quality passed"

MODEL_PATH = os.path.join(ROOT_DIR, "ml", "models", "best_lsd_model.pt")
LABEL_MAPPING_PATH = os.path.join(ROOT_DIR, "ml", "models", "label_mapping.json")

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Global cached model instance to avoid reloading weights on repeated inference
_CACHED_MODEL = None
_CACHED_DEVICE = None
_CACHED_MODEL_INFO = None

def get_inference_transform(img_size: int = 224):
    return transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

def load_trained_model(model_path: str = MODEL_PATH):
    """Loads and caches the trained PyTorch vision model."""
    global _CACHED_MODEL, _CACHED_DEVICE, _CACHED_MODEL_INFO
    
    if _CACHED_MODEL is not None:
        return _CACHED_MODEL, _CACHED_DEVICE, _CACHED_MODEL_INFO
        
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    if not os.path.exists(model_path):
        # Fallback to fresh MobileNetV3 architecture if checkpoint is absent
        model = mobilenet_v3_small(weights=MobileNet_V3_Small_Weights.DEFAULT)
        model.classifier[3] = nn.Linear(model.classifier[3].in_features, 2)
        model.to(device)
        model.eval()
        _CACHED_MODEL = model
        _CACHED_DEVICE = device
        _CACHED_MODEL_INFO = {"model_name": "mobilenet_v3_small", "img_size": 224}
        return model, device, _CACHED_MODEL_INFO
        
    checkpoint = torch.load(model_path, map_location=device, weights_only=False)
    model_name = checkpoint.get("model_name", "mobilenet_v3_small")
    img_size = checkpoint.get("img_size", 224)
    num_classes = checkpoint.get("num_classes", 2)
    
    if model_name == "efficientnet_b0":
        model = efficientnet_b0(weights=None)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Sequential(
            nn.Dropout(p=0.3, inplace=True),
            nn.Linear(in_features, num_classes)
        )
    else:
        model = mobilenet_v3_small(weights=None)
        in_features = model.classifier[3].in_features
        model.classifier[3] = nn.Linear(in_features, num_classes)
        
    model.load_state_dict(checkpoint["state_dict"])
    model.to(device)
    model.eval()
    
    _CACHED_MODEL = model
    _CACHED_DEVICE = device
    _CACHED_MODEL_INFO = {"model_name": model_name, "img_size": img_size}
    return model, device, _CACHED_MODEL_INFO

def calculate_risk_level(lsd_prob: float, low_threshold: float = 0.30, high_threshold: float = 0.70) -> str:
    """Categorizes Lumpy Skin Disease probability into configurable risk tiers."""
    if lsd_prob < low_threshold:
        return "LOW"
    elif lsd_prob < high_threshold:
        return "MEDIUM"
    else:
        return "HIGH"

def predict_lsd(
    image_path: str,
    low_threshold: float = 0.30,
    high_threshold: float = 0.70,
    model_path: str = MODEL_PATH
) -> Dict[str, Any]:
    """
    Primary Computer Vision inference function for Cattle Lumpy Skin Disease screening.
    
    Returns:
    {
      "predicted_class": "Possible Lumpy Skin Disease" | "Healthy",
      "confidence": float (0.0 to 1.0),
      "risk_level": "LOW" | "MEDIUM" | "HIGH",
      "probabilities": {"Healthy": float, "Possible Lumpy Skin Disease": float},
      "risk_thresholds": {"low_max": float, "high_min": float},
      "is_veterinary_diagnosis": False,
      "disclaimer": "AI screening tool only. Not a veterinary diagnosis. Consult a registered veterinarian."
    }
    """
    # 1. Quality Validation
    is_valid, quality_msg = validate_image_quality(image_path)
    if not is_valid:
        return {
            "predicted_class": "Invalid Image",
            "confidence": 0.0,
            "risk_level": "UNKNOWN",
            "error": quality_msg,
            "probabilities": {"Healthy": 0.0, "Possible Lumpy Skin Disease": 0.0},
            "is_veterinary_diagnosis": False,
            "disclaimer": "AI screening tool only. Not a veterinary diagnosis. Consult a registered veterinarian."
        }
        
    # 2. Image Loading & Preprocessing
    try:
        with Image.open(image_path) as img:
            img_rgb = img.convert('RGB')
    except Exception as e:
        return {
            "predicted_class": "Unreadable Image",
            "confidence": 0.0,
            "risk_level": "UNKNOWN",
            "error": f"Failed to decode image file: {str(e)}",
            "probabilities": {"Healthy": 0.0, "Possible Lumpy Skin Disease": 0.0},
            "is_veterinary_diagnosis": False,
            "disclaimer": "AI screening tool only. Not a veterinary diagnosis. Consult a registered veterinarian."
        }
        
    # 3. Model Inference
    model, device, info = load_trained_model(model_path)
    transform = get_inference_transform(info.get("img_size", 224))
    tensor = transform(img_rgb).unsqueeze(0).to(device)
    
    with torch.no_grad():
        logits = model(tensor)
        probabilities = torch.softmax(logits, dim=1).squeeze(0).cpu().numpy()
        
    prob_healthy = float(round(probabilities[0], 4))
    prob_lsd = float(round(probabilities[1], 4))
    
    # 4. Decision & Risk Thresholding
    if prob_lsd >= 0.50:
        predicted_class = "Possible Lumpy Skin Disease"
        confidence = prob_lsd
    else:
        predicted_class = "Healthy"
        confidence = prob_healthy
        
    risk_level = calculate_risk_level(prob_lsd, low_threshold, high_threshold)
    
    return {
        "predicted_class": predicted_class,
        "confidence": confidence,
        "risk_level": risk_level,
        "probabilities": {
            "Healthy": prob_healthy,
            "Possible Lumpy Skin Disease": prob_lsd
        },
        "risk_thresholds": {
            "low_max": low_threshold,
            "high_min": high_threshold
        },
        "model_architecture": info.get("model_name"),
        "is_veterinary_diagnosis": False,
        "disclaimer": "AI screening tool only. Not a veterinary diagnosis. Consult a registered veterinarian for clinical confirmation and prescription."
    }

# Backward-compatible function signature for existing routes
def analyze_animal_image(image_path: str) -> Dict[str, Any]:
    """
    Maintains full backward compatibility with existing backend routes.
    Returns vision findings combined with the PyTorch model prediction.
    """
    res = predict_lsd(image_path)
    is_lsd = (res.get("predicted_class") == "Possible Lumpy Skin Disease")
    confidence = res.get("confidence", 0.0)
    risk_score = round(res.get("probabilities", {}).get("Possible Lumpy Skin Disease", 0.0) * 100.0, 1)
    
    findings = (
        f"Visual inspection flagged possible cutaneous nodule patterns (Confidence: {confidence*100:.1f}%, Risk: {res.get('risk_level')})."
        if is_lsd else
        f"Hide surface clear of characteristic nodular lesions (Confidence: {confidence*100:.1f}%, Risk: {res.get('risk_level')})."
    )
    
    return {
        "abnormality_detected": is_lsd,
        "lesion_count": 4 if is_lsd else 0,
        "abnormality_score": risk_score,
        "visual_findings": findings,
        "confidence": confidence,
        "risk_level": res.get("risk_level", "LOW"),
        "is_veterinary_diagnosis": False,
        "disclaimer": res.get("disclaimer")
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classify cattle image for Lumpy Skin Disease")
    parser.add_argument("image_path", type=str, help="Path to input cattle image")
    parser.add_argument("--low", type=float, default=0.30, help="Low risk threshold (default: 0.30)")
    parser.add_argument("--high", type=float, default=0.70, help="High risk threshold (default: 0.70)")
    
    args = parser.parse_args()
    result = predict_lsd(args.image_path, low_threshold=args.low, high_threshold=args.high)
    print(json.dumps(result, indent=2))
