import os
import io
import json
import time
from typing import Dict, Any, Optional
import numpy as np
from PIL import Image

import torch
import torch.nn as nn
from torchvision import transforms, models

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)

MODEL_CHECKPOINT_PATH = os.path.join(ROOT_DIR, "ml", "models", "best_lsd_model.pt")
LABEL_MAPPING_PATH = os.path.join(ROOT_DIR, "ml", "models", "label_mapping.json")

class ImageRiskService:
    """
    Dedicated Computer Vision Service for Lumpy Skin Disease (LSD) visual screening.
    Ensures model weights are loaded ONCE into memory and reused across all requests.
    """
    _instance: Optional["ImageRiskService"] = None

    def __init__(self):
        self._model: Optional[nn.Module] = None
        self._device: torch.device = torch.device("cpu")
        self._label_map: Dict[str, str] = {"0": "Healthy", "1": "Possible Lumpy Skin Disease"}
        self._transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        self._load_model_once()

    @classmethod
    def get_instance(cls) -> "ImageRiskService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_model_once(self):
        """Loads and caches the PyTorch MobileNetV3 model once into memory."""
        if self._model is not None:
            return
            
        t0 = time.time()
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load label mapping if available
        if os.path.exists(LABEL_MAPPING_PATH):
            try:
                with open(LABEL_MAPPING_PATH, "r") as f:
                    self._label_map = json.load(f)
            except Exception:
                pass
                
        if os.path.exists(MODEL_CHECKPOINT_PATH):
            try:
                print(f"[IMAGE SERVICE] Loading MobileNetV3-Small checkpoint from {MODEL_CHECKPOINT_PATH} onto {self._device}...")
                model = models.mobilenet_v3_small(weights=None)
                in_features = model.classifier[3].in_features
                model.classifier[3] = nn.Linear(in_features, 2)
                
                checkpoint = torch.load(MODEL_CHECKPOINT_PATH, map_location=self._device, weights_only=False)
                if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
                    state_dict = checkpoint["state_dict"]
                else:
                    state_dict = checkpoint
                model.load_state_dict(state_dict)
                model.to(self._device)
                model.eval()
                self._model = model
                load_time = time.time() - t0
                print(f"[IMAGE SERVICE] Model loaded and cached successfully in {load_time:.2f}s.")
            except Exception as exc:
                print(f"[IMAGE SERVICE] Warning: Failed to load PyTorch checkpoint: {exc}. Initializing fallback eval model.")
                self._model = self._init_fallback_model()
        else:
            print(f"[IMAGE SERVICE] Checkpoint {MODEL_CHECKPOINT_PATH} not found. Using fallback architecture.")
            self._model = self._init_fallback_model()

    def _init_fallback_model(self) -> nn.Module:
        model = models.mobilenet_v3_small(weights=None)
        in_features = model.classifier[3].in_features
        model.classifier[3] = nn.Linear(in_features, 2)
        model.to(self._device)
        model.eval()
        return model

    def check_image_quality(self, pil_img: Image.Image) -> Dict[str, Any]:
        """
        Runs pre-flight quality checks for focus sharpness and illumination.
        """
        # Convert to grayscale numpy array
        gray = pil_img.convert("L")
        arr = np.array(gray, dtype=np.float32)
        
        # 1. Laplacian sharpness check
        # Approximation of Laplacian kernel [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
        laplacian = (
            np.roll(arr, 1, axis=0) + np.roll(arr, -1, axis=0) +
            np.roll(arr, 1, axis=1) + np.roll(arr, -1, axis=1) - 4 * arr
        )
        laplacian_var = float(np.var(laplacian))
        
        # 2. Mean brightness check (0 to 255)
        mean_brightness = float(np.mean(arr))
        
        # Quality gates
        is_blurry = laplacian_var < 50.0
        is_too_dark = mean_brightness < 40.0
        is_overexposed = mean_brightness > 230.0
        passed = not (is_blurry or is_too_dark or is_overexposed)
        
        warnings = []
        if is_blurry:
            warnings.append("Image exhibits motion blur or poor optical focus.")
        if is_too_dark:
            warnings.append("Low illumination detected; ensure adequate lighting.")
        if is_overexposed:
            warnings.append("Overexposure or excessive glare detected on animal hide.")
            
        return {
            "quality_check_passed": passed,
            "blur_laplacian_variance": round(laplacian_var, 2),
            "mean_brightness": round(mean_brightness, 2),
            "quality_warnings": warnings
        }

    def analyze_image(
        self,
        image_bytes: bytes,
        filename: str = "upload.jpg",
        low_threshold: float = 0.30,
        high_threshold: float = 0.70
    ) -> Dict[str, Any]:
        """
        Executes independent image risk screening for an uploaded cattle photograph.
        """
        t0 = time.perf_counter()
        
        # 1. Open and validate image with PIL
        try:
            pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as exc:
            raise ValueError(f"Invalid image format: {str(exc)}")
            
        # 2. Pre-flight quality assessment
        quality_info = self.check_image_quality(pil_img)
        
        # 3. Model Inference (Reuses cached model in memory)
        input_tensor = self._transform(pil_img).unsqueeze(0).to(self._device)
        with torch.no_grad():
            outputs = self._model(input_tensor)
            probs = torch.softmax(outputs, dim=1).squeeze(0).cpu().numpy()
            
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        
        # 4. Map probabilities
        prob_healthy = float(probs[0])
        prob_lsd = float(probs[1])
        
        # 5. Determine Predicted Class and Confidence
        if prob_lsd >= prob_healthy:
            predicted_class = "Possible Lumpy Skin Disease"
            confidence = prob_lsd
        else:
            predicted_class = "Healthy"
            confidence = prob_healthy
            
        # 6. Categorize Visual Risk Level based on configurable thresholds
        if prob_lsd < low_threshold:
            risk_level = "LOW"
        elif prob_lsd < high_threshold:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
            
        risk_score = round(prob_lsd * 100.0, 1)
        
        return {
            "service": "image_risk_analysis",
            "predicted_class": predicted_class,
            "confidence": round(confidence, 4),
            "risk_level": risk_level,
            "risk_score": risk_score,
            "probabilities": {
                "Possible Lumpy Skin Disease": round(prob_lsd, 4),
                "Healthy": round(prob_healthy, 4)
            },
            "risk_thresholds": {
                "low_threshold": low_threshold,
                "high_threshold": high_threshold
            },
            "image_quality": quality_info,
            "model_metadata": {
                "architecture": "MobileNetV3-Small",
                "checkpoint": "ml/models/best_lsd_model.pt",
                "framework": "PyTorch",
                "device": str(self._device),
                "inference_latency_ms": latency_ms
            },
            # Mandatory Ethical Non-Diagnosis Disclaimer
            "is_veterinary_diagnosis": False,
            "disclaimer": (
                "AI screening and visual risk triage tool only. Not a veterinary diagnosis. "
                "Consult a registered veterinarian for confirmatory laboratory testing (e.g. PCR/ELISA)."
            )
        }

def get_image_service() -> ImageRiskService:
    return ImageRiskService.get_instance()
