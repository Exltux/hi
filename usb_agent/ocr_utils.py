from typing import Optional
from PIL import Image
import pytesseract


def extract_text(image_path: str) -> Optional[str]:
    try:
        img = Image.open(image_path)
        return pytesseract.image_to_string(img)
    except Exception:
        return None
