"""
Đọc chữ từ ảnh chụp màn hình (topic / comment) bằng Tesseract OCR.

Cài đặt cần thiết (Ubuntu/Debian):
    sudo apt install tesseract-ocr tesseract-ocr-vie

macOS (brew):
    brew install tesseract tesseract-lang
"""
from pathlib import Path
import pytesseract
from PIL import Image, ImageOps, ImageFilter

from config import CFG


def _preprocess(img: Image.Image) -> Image.Image:
    """Tiền xử lý nhẹ để tăng độ chính xác OCR trên ảnh chụp màn hình
    (nền trắng/đen, chữ tương đối rõ)."""
    img = img.convert("L")               # grayscale
    img = ImageOps.autocontrast(img)     # tăng tương phản
    img = img.filter(ImageFilter.SHARPEN)
    return img


def extract_text(image_path: Path) -> str:
    img = Image.open(image_path)
    img = _preprocess(img)

    raw = pytesseract.image_to_string(img, lang=CFG.ocr_lang, config="--psm 6")
    # Gộp khoảng trắng/newline thừa
    text = " ".join(raw.split())
    return text.strip()
