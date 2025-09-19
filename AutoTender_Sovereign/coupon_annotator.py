from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageDraw, ImageFont
import io

def create_annotation_overlay(annotations, signature_path, signature_coords):
    """
    Creates a PDF overlay with the specified text annotations and signature.
    """
    packet = io.BytesIO()
    # Create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)

    # Add text annotations
    for text, coords in annotations.items():
        can.drawString(coords[0], coords[1], text)

    # Add signature
    if signature_path and signature_coords:
        try:
            with Image.open(signature_path) as signature_img:
                # Assuming the signature image has a transparent background
                can.drawImage(signature_path, signature_coords[0], signature_coords[1], width=100, height=50, mask='auto')
        except FileNotFoundError:
            print(f"Signature file not found at {signature_path}")

    can.save()

    # Move to the beginning of the StringIO buffer
    packet.seek(0)
    return packet

def annotate_pdf_coupon(input_pdf_path, output_pdf_path, annotations, signature_path, signature_coords):
    """
    Annotates a PDF coupon with text and a signature.
    """
    overlay_pdf_packet = create_annotation_overlay(annotations, signature_path, signature_coords)

    overlay_pdf = PdfReader(overlay_pdf_packet)
    existing_pdf = PdfReader(open(input_pdf_path, "rb"))
    output = PdfWriter()

    # Add the "watermark" (our annotations) to the existing page
    page = existing_pdf.pages[0]
    page.merge_page(overlay_pdf.pages[0])
    output.add_page(page)

    # Write the result to a new PDF file
    with open(output_pdf_path, "wb") as outputStream:
        output.write(outputStream)

    print(f"Successfully annotated PDF and saved to {output_pdf_path}")

def annotate_image_coupon(input_image_path, output_image_path, annotations, signature_text, signature_coords):
    """
    Annotates an image-based coupon with text and a typed signature.
    """
    try:
        image = Image.open(input_image_path)
        draw = ImageDraw.Draw(image)

        # You may need to specify a path to a .ttf font file.
        try:
            font = ImageFont.truetype("arial.ttf", 80)
        except IOError:
            font = ImageFont.load_default()

        # Add text annotations
        for text, coords in annotations.items():
            draw.text(coords, text, fill="black", font=font)

        # Add typed signature
        if signature_text and signature_coords:
            try:
                signature_font = ImageFont.truetype("arial.ttf", 90)
            except IOError:
                signature_font = ImageFont.load_default()
            draw.text(signature_coords, signature_text, fill="blue", font=signature_font)

        image.save(output_image_path)
        print(f"Successfully annotated image and saved to {output_image_path}")

    except FileNotFoundError:
        print(f"Input image file not found at {input_image_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    # --- Example Usage for Image Annotation ---

    # 1. Define the input and output files
    input_coupon_image = "/home/mrnam205/Desktop/try2/credit-card-statement-example-scaled.jpg"
    output_coupon_image = "/home/mrnam205/Desktop/try2/annotated-credit-card-statement.jpg"

    # 2. Define the annotations (text and coordinates)
    # The coordinates (x, y) are measured from the top-left corner of the image.
    payment_annotations = {
        "Pay to the order of: GENERIC CREDIT CARD": (100, 2000),
        "Amount: $250.00": (100, 2080),
        "Tendered under UCC §3-104 and §3-603(b).": (100, 2160),
        "Refusal to accept without written cause may result in discharge of obligation.": (100, 2240),
    }

    # 3. Define the signature details
    signature = "/s/ john-doe:smith, beneficiary"
    signature_coordinates = (100, 2340)  # (x, y) coordinates for the signature

    # 4. Annotate the Image
    annotate_image_coupon(input_coupon_image, output_coupon_image, payment_annotations, signature, signature_coordinates)