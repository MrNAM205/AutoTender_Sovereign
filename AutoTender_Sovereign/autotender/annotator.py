import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any, Union
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pypdf import PdfReader, PdfWriter

import deepdoctection as dd

# --- Logging setup ---
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Initialize DeepDoctection analyzer once
# This will download models the first time it's run
try:
    analyzer = dd.get_dd_analyzer()
    logger.info("DeepDoctection analyzer initialized.")
except Exception as e:
    logger.error(f"Failed to initialize DeepDoctection analyzer: {e}")
    analyzer = None # Set to None if initialization fails


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

    document_obj = None
    if analyzer:
        try:
            # DeepDoctection analyze expects a path or a PIL Image
            document_obj = analyzer.analyze(path=str(input_file))
            logger.info("DeepDoctection analysis complete for image.")
        except Exception as e:
            logger.error(f"DeepDoctection analysis failed for image: {e}")

    draw = ImageDraw.Draw(img)
    for ann in config.get("annotations", []):
        font = get_font(ann.get("size", 12), ann.get("font"))
        color = ann.get("color", "red")
        text = ann["text"]

        x, y = ann.get("x", 50), ann.get("y", 50) # Default to manual placement

        if "field" in ann and document_obj:
            # Find the bounding box of the field using DeepDoctection's document object
            # This is a simplified example; actual field detection might be more complex
            # and involve iterating through document_obj.get_annotation(category_name="TEXT")
            # or similar methods to find specific text blocks.
            # For now, we'll simulate by looking for a text block that contains the field name.
            
            # DeepDoctection's layout objects have .text and .bounding_box
            found_field_box = None
            for block in document_obj.get_annotation(category_name="TEXT"):
                if ann["field"].lower() in block.text.lower():
                    found_field_box = block.bounding_box
                    break
            
            if found_field_box:
                # DeepDoctection coordinates are (x1, y1, x2, y2)
                # PIL coordinates are (x, y) from top-left
                # We'll use the top-left of the found field
                x_field, y_field = found_field_box[0], found_field_box[1]
                x = x_field + ann.get("offset_x", 0)
                y = y_field + ann.get("offset_y", 0)
            else:
                logger.warning(f"Field '{ann['field']}' not found, using default coords")
        
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
        
        for page_number, page in enumerate(reader.pages):
            document_obj = None
            if analyzer:
                try:
                    # DeepDoctection can analyze PDF pages directly
                    # For multi-page PDFs, we might need to pass individual pages or a range
                    # For simplicity, we'll analyze the whole PDF once and then get page-specific info
                    # This part needs refinement for page-specific layout detection
                    if page_number == 0: # Analyze only once for the whole document
                        document_obj = analyzer.analyze(path=str(input_file))
                        logger.info("DeepDoctection analysis complete for PDF.")
                except Exception as e:
                    logger.error(f"DeepDoctection analysis failed for PDF: {e}")

            # Create an in-memory overlay
            packet = BytesIO()
            # ReportLab uses bottom-left origin, so we need to convert PIL top-left y to ReportLab y
            # Assuming letter size for now, need to get actual page size from PDF
            page_width = page.mediabox.width
            page_height = page.mediabox.height
            c = canvas.Canvas(packet, pagesize=(page_width, page_height))

            # Apply annotations to the canvas
            # Need to adjust y-coordinates for ReportLab's bottom-left origin
            # This is a simplified conversion; actual conversion needs to consider font size and text height
            
            for ann in config.get("annotations", []):
                font = get_font(ann.get("size", 12), ann.get("font"))
                color = ann.get("color", "red")
                text = ann["text"]

                x, y = ann.get("x", 50), ann.get("y", 50) # Default to manual placement

                if "field" in ann and document_obj:
                    found_field_box = None
                    for block in document_obj.get_annotation(category_name="TEXT"):
                        if ann["field"].lower() in block.text.lower():
                            found_field_box = block.bounding_box
                            break
                    
                    if found_field_box:
                        x_field, y_field = found_field_box[0], found_field_box[1]
                        x = x_field + ann.get("offset_x", 0)
                        # Convert PIL top-left y to ReportLab bottom-left y
                        y = page_height - (y_field + ann.get("offset_y", 0))
                    else:
                        logger.warning(f"Field '{ann['field']}' not found on page {page_number + 1}, using default coords")
                else:
                    # Convert PIL top-left y to ReportLab bottom-left y for manual placement
                    y = page_height - y

                c.setFont("Helvetica", ann.get("size", 12))
                if color.lower() == "red": c.setFillColorRGB(1, 0, 0)
                elif color.lower() == "blue": c.setFillColorRGB(0, 0, 1)
                else: c.setFillColorRGB(0, 0, 0) # default to black
                c.drawString(x, y, ann["text"])

            c.save()
            packet.seek(0)

            # Merge overlay with the existing page
            overlay_reader = PdfReader(packet)
            pdf_page = reader.pages[page_number] # Get the original page object
            pdf_page.merge_page(overlay_reader.pages[0])
            writer.add_page(pdf_page)

    with open(output_file, "wb") as f_out:
        writer.write(f_out)

    logger.info(f"Annotated PDF saved to {output_file}")


# --- Main Entrypoint ---
def annotate(
    input_file: Union[str, Path],
    output_file: Union[str, Path],
    config_path: Optional[Union[str, Path]] = None,
):
    """Auto-detect input type and apply annotations (DeepDoctection-aware)."""
    if not analyzer:
        logger.error("DeepDoctection analyzer not initialized. Cannot proceed with annotation.")
        return

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