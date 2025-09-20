import argparse
import datetime
from io import BytesIO
import os

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def get_font(font_name, size):
    try:
        return ImageFont.truetype(font_name, size)
    except IOError:
        return ImageFont.load_default()

def annotate_image(input_path, output_path, endorsement_lines, signature, x, y):
    """
    Annotates an image with a multi-line endorsement, with a white-out box.
    """
    try:
        image = Image.open(input_path)
        draw = ImageDraw.Draw(image)

        font_regular = get_font("arial.ttf", 25)
        font_bold = get_font("arialbd.ttf", 30)

        # Calculate text block size
        max_width = 0
        total_height = 0
        line_spacing = 10
        for line in endorsement_lines:
            # This is a simplification; proper width calculation is more complex
            max_width = max(max_width, len(line) * 15) 
            total_height += font_regular.getbbox(line)[3] + line_spacing
        total_height += font_regular.getbbox(signature)[3] + line_spacing # Add space for signature and date

        # Draw white-out box
        box_margin = 20
        draw.rectangle((x - box_margin, y - box_margin, x + max_width + box_margin, y + total_height + box_margin), fill="white")

        # Text layout
        current_y = y
        for line in endorsement_lines:
            font_to_use = font_bold if line.startswith("**") else font_regular
            draw.text((x, current_y), line.replace("**", ""), fill="black", font=font_to_use)
            current_y += font_regular.getbbox(line)[3] + line_spacing

        # Signature
        current_y += line_spacing
        draw.text((x, current_y), signature, fill="blue", font=get_font("arial.ttf", 35))
        current_y += font_regular.getbbox(signature)[3] + line_spacing

        # Date
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        draw.text((x, current_y), f"Date: {date_str}", fill="black", font=font_regular)

        image.save(output_path)
        print(f"Successfully annotated image and saved to {output_path}")

    except Exception as e:
        print(f"An error occurred during image annotation: {e}")

def annotate_pdf(input_path, output_path, endorsement_lines, signature, x, y):
    """
    Annotates a PDF with a multi-line endorsement, with a white-out box.
    """
    try:
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)

        # This is a simplified white-out box for PDF
        can.setFillColorRGB(1, 1, 1)
        can.rect(x, y - 150, 500, 150, fill=1, stroke=0)

        can.setFillColorRGB(0, 0, 0)
        text_object = can.beginText(x, y)
        
        for line in endorsement_lines:
            font_name = "Helvetica-Bold" if line.startswith("**") else "Helvetica"
            text_object.setFont(font_name, 10)
            text_object.textLine(line.replace("**", ""))
        
        text_object.setFont("Helvetica", 12)
        text_object.textLine("")
        text_object.textLine(signature)
        text_object.textLine(f"Date: {datetime.date.today().strftime('%Y-%m-%d')}")

        can.drawText(text_object)
        can.save()
        packet.seek(0)

        overlay = PdfReader(packet)
        existing_pdf = PdfReader(open(input_path, "rb"))
        output = PdfWriter()

        page = existing_pdf.pages[0]
        page.merge_page(overlay.pages[0])
        output.add_page(page)

        with open(output_path, "wb") as f:
            output.write(f)
        print(f"Successfully annotated PDF and saved to {output_path}")

    except Exception as e:
        print(f"An error occurred during PDF annotation: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Annotate a bill with a sovereign endorsement.")
    parser.add_argument("--input", required=True, help="Path to the input bill (PDF or image).")
    parser.add_argument("--output", help="Path to save the annotated bill. If not provided, defaults to [input]_annotated.[ext]")
    parser.add_argument("--x", type=int, default=100, help="X-coordinate for the top-left of the endorsement block.")
    parser.add_argument("--y", type=int, default=1950, help="Y-coordinate for the top-left of the endorsement block.")
    parser.add_argument("--signature", required=True, help="The signature text to apply.")
    parser.add_argument('--lines', nargs='+', required=True, help='The lines of the endorsement text. Use "" for blank lines. Prefix with ** for bold.')

    args = parser.parse_args()

    # Determine output path if not provided
    if not args.output:
        file_name, file_ext = os.path.splitext(args.input)
        args.output = f"{file_name}_annotated{file_ext}"

    # Determine file type and annotate
    file_ext = os.path.splitext(args.input)[1].lower()
    if file_ext in [".pdf"]:
        # PDF coordinates are from bottom-left, so we need to adjust
        # This is a simplistic adjustment and may need refinement
        pdf_y = 800 - args.y / 2 # A rough conversion
        annotate_pdf(args.input, args.output, args.lines, args.signature, args.x, pdf_y)
    elif file_ext in [".png", ".jpg", ".jpeg"]:
        annotate_image(args.input, args.output, args.lines, args.signature, args.x, args.y)
    else:
        print(f"Error: Unsupported file type '{file_ext}'. Please use a PDF or image file.")
