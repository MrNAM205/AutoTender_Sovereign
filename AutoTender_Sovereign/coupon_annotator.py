from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageDraw, ImageFont
import io
import datetime

def create_annotation_overlay(annotations, signature_path, signature_coords):
    """
    Creates a PDF overlay with the specified text annotations and signature.
    """
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    for text, coords in annotations.items():
        can.drawString(coords[0], coords[1], text)
    if signature_path and signature_coords:
        try:
            with Image.open(signature_path) as signature_img:
                can.drawImage(signature_path, signature_coords[0], signature_coords[1], width=100, height=50, mask='auto')
        except FileNotFoundError:
            print(f"Signature file not found at {signature_path}")
    can.save()
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
    page = existing_pdf.pages[0]
    page.merge_page(overlay_pdf.pages[0])
    output.add_page(page)
    with open(output_pdf_path, "wb") as outputStream:
        output.write(outputStream)
    print(f"Successfully annotated PDF and saved to {output_pdf_path}")

def annotate_image_coupon(input_image_path, output_image_path, endorsement_lines, signature_text, signature_coords, date_coords):
    """
    Annotates an image with an inline endorsement.
    """
    try:
        image = Image.open(input_image_path)
        draw = ImageDraw.Draw(image)

        # Fonts
        try:
            font_regular = ImageFont.truetype("arial.ttf", 25)
        except IOError:
            font_regular = ImageFont.load_default()
        
        try:
            font_bold = ImageFont.truetype("arialbd.ttf", 30)
        except IOError:
            font_bold = font_regular

        # Endorsement lines
        for text, coords, is_bold in endorsement_lines:
            font_to_use = font_bold if is_bold else font_regular
            draw.text(coords, text, fill="black", font=font_to_use)

        # Signature
        try:
            signature_font = ImageFont.truetype("arial.ttf", 35)
        except IOError:
            signature_font = font_regular
        draw.text(signature_coords, signature_text, fill="blue", font=signature_font)

        # Date
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        draw.text(date_coords, f"Date: {date_str}", fill="black", font=font_regular)

        image.save(output_image_path)
        print(f"Successfully annotated image and saved to {output_image_path}")

    except FileNotFoundError:
        print(f"Input image file not found at {input_image_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    input_image = "/home/mrnam205/Desktop/try2/credit-card-statement-example-scaled.jpg"
    output_image = "/home/mrnam205/Desktop/try2/annotated-credit-card-statement-refined.jpg"
    
    lines = [
        ("Pay to the Order of: GENERIC CREDIT CARD", (100, 1950), True),
        ("Amount: $250.00", (100, 1990), True),
        ("", (100, 2020), False),
        ("For Value Received; Accepted for Settlement and Closure.", (100, 2050), False),
        ("Tendered for discharge of obligation per UCC § 3-603(b).", (100, 2080), False),
        ("This instrument is to be negotiated per UCC § 3-104 and § 3-204.", (100, 2110), False),
        ("Acceptance by deposit or non-response is governed by UCC § 3-409 and the Mailbox Rule.", (100, 2140), False),
        ("Dishonor of this tender will be reported per IRS Publications and may result in the issuance of Form 1099-C.", (100, 2170), False),
        ("Without Prejudice, UCC 1-308.", (100, 2200), False),
    ]
    
    signature = "/s/ john-doe:smith, beneficiary"
    sig_coords = (100, 2250)
    dt_coords = (100, 2300)

    annotate_image_coupon(input_image, output_image, lines, signature, sig_coords, dt_coords)