import os
import io
import uuid
import random
import string
import base64
from typing import Tuple
import qrcode
from config import settings

QR_STORAGE_DIR = os.path.join(settings.UPLOAD_DIR, "qrcodes")
os.makedirs(QR_STORAGE_DIR, exist_ok=True)

def generate_unique_animal_id(species: str = "Cattle", district: str = "MH") -> str:
    """
    Generates an official, human-readable National Livestock Ear-Tag Identifier.
    Format: TAG-<STATE/DISTRICT>-<YEAR>-<5-CHAR-HEX>
    Example: TAG-MH-2026-A8F24
    """
    clean_dist = "".join(filter(str.isalnum, (district or "MH").upper()))[:3]
    year = "2026"
    random_suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"TAG-{clean_dist}-{year}-{random_suffix}"

def generate_qr_identifier() -> str:
    """
    Generates a unique cryptographic QR token identifier.
    Format: QR-SENTINEL-<UUID4_HEX>
    """
    token_hex = uuid.uuid4().hex[:12].upper()
    return f"QR-SENTINEL-{token_hex}"

def generate_qr_code_assets(payload_text: str, animal_id: str) -> Tuple[str, str]:
    """
    Generates both a stored PNG image asset and a Base64 data URI for instant web rendering.
    Returns: (file_url, base64_data_uri)
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3
    )
    qr.add_data(payload_text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1E3A8A", back_color="#FFFFFF") # Sentinel Navy on White
    
    # 1. Save PNG file to uploads/qrcodes/
    clean_tag = animal_id.replace("-", "_").replace(" ", "_").lower()
    filename = f"qr_{clean_tag}_{uuid.uuid4().hex[:6]}.png"
    file_path = os.path.join(QR_STORAGE_DIR, filename)
    img.save(file_path, format="PNG")
    file_url = f"/uploads/qrcodes/{filename}"
    
    # 2. Generate Base64 Data URI
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64_encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    b64_data_uri = f"data:image/png;base64,{b64_encoded}"
    
    return file_url, b64_data_uri
