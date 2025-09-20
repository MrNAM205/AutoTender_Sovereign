import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any, Union, List
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pypdf import PdfReader, PdfWriter

# --- Logging setup ---
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


# --- Config Loader ---
def load_config(config_path: Optional[Union[str, Path]]) -> Dict[str, Any]:
    """Load annotation config (JSON) or return defaults."""
    if config_path is None:
        logger.warning("No config provided, using defaults")
        return {
            "annotations": [
                {"text": "SAMPLE", "x": 50, "y": 50, "size": 14, "color": "red"}
            ]
        }

    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    if "annotations" not in cfg or not isinstance(cfg["annotations"], list):
        raise ValueError("Invalid config: must contain 'annotations' list")

    return cfg


# --- Font Loader ---
def get_font(size: int, font_path: Optional[str] = None) -> ImageFont.ImageFont:
    """Try to load a TTF font, fall back to default."""
    try:
        if font_path:
            return ImageFont.truetype(font_path, size)
    except Exception as e:
        logger.warning(f"Font load failed ({font_path}): {e}")
    return ImageFont.load_default()


# --- Image Annotation ---
def annotate_image(
    input_file: Union[str, Path],
    output_file: Union[str, Path],
    config: Dict[str, Any],
):
    """Annotate an image file (JPG, PNG)."""
    img = Image.open(input_file).convert("RGB")
    draw = ImageDraw.Draw(img)

    for ann in config.get("annotations", []):
        font = get_font(ann.get("size", 12), ann.get("font"))
        color = ann.get("color", "red")
        text = ann["text"]
        x, y = ann["x"], ann["y"]
        draw.text((x, y), text, fill=color, font=font)

    img.save(output_file)
    logger.info(f"Annotated image saved to {output_file}")


# --- PDF Annotation ---
def annotate_pdf(
    input_file: Union[str, Path],
    output_file: Union[str, Path],
    config: Dict[str, Any],
):
    """Annotate a PDF by overlaying text on each page."""
    writer = PdfWriter()
    
    with open(input_file, "rb") as f_in:
        reader = PdfReader(f_in)
        
        for page in reader.pages:
            # Create an in-memory overlay
            packet = BytesIO()
            c = canvas.Canvas(packet, pagesize=letter)

            for ann in config.get("annotations", []):
                c.setFont("Helvetica", ann.get("size", 12))
                color = ann.get("color", "red")
                if color.lower() == "red": c.setFillColorRGB(1, 0, 0)
                elif color.lower() == "blue": c.setFillColorRGB(0, 0, 1)
                else: c.setFillColorRGB(0, 0, 0) # default to black
                c.drawString(ann["x"], ann["y"], ann["text"])

            c.save()
            packet.seek(0)

            # Merge overlay with the existing page
            overlay_reader = PdfReader(packet)
            page.merge_page(overlay_reader.pages[0])
            writer.add_page(page)

    with open(output_file, "wb") as f_out:
        writer.write(f_out)

    logger.info(f"Annotated PDF saved to {output_file}")


# --- Main Entrypoint ---
def annotate(
    input_file: Union[str, Path],
    output_file: Union[str, Path],
    config_path: Optional[Union[str, Path]] = None,
):
    """Auto-detect input type and apply annotations."""
    config = load_config(config_path)
    input_file = Path(input_file)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    ext = input_file.suffix.lower()
    if ext in [".jpg", ".jpeg", ".png"]:
        annotate_image(input_file, output_file, config)
    elif ext == ".pdf":
        annotate_pdf(input_file, output_file, config)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
