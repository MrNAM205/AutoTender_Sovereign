import argparse
import os
from pypdf import PdfReader

def scan_pdf(file_path, keywords):
    """
    Scans a PDF file for a list of keywords.
    """
    try:
        reader = PdfReader(file_path)
        found_keywords = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                for keyword in keywords:
                    if keyword.lower() in text.lower():
                        if keyword not in found_keywords:
                            found_keywords.append(keyword)
        return found_keywords
    except Exception as e:
        print(f"Error reading or scanning PDF: {e}")
        return []

def scan_image(file_path, keywords):
    """
    Scans an image file for a list of keywords using OCR.
    """
    try:
        import pytesseract
        from PIL import Image

        text = pytesseract.image_to_string(Image.open(file_path))
        found_keywords = []
        for keyword in keywords:
            if keyword.lower() in text.lower():
                if keyword not in found_keywords:
                    found_keywords.append(keyword)
        return found_keywords
    except ImportError:
        print("Error: pytesseract library not found. Please install it.")
        return []
    except Exception as e:
        print(f"An error occurred during image OCR: {e}")
        return []

def scan_txt(file_path, keywords):
    """
    Scans a text file for a list of keywords.
    """
    try:
        with open(file_path, 'r') as f:
            text = f.read()
        found_keywords = []
        for keyword in keywords:
            if keyword.lower() in text.lower():
                if keyword not in found_keywords:
                    found_keywords.append(keyword)
        return found_keywords
    except Exception as e:
        print(f"Error reading or scanning text file: {e}")
        return []

def scan(file_path, keywords):
    """
    Main function to scan a document for keywords.
    Returns a list of found keywords.
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    found = []
    if file_ext == ".pdf":
        found = scan_pdf(file_path, keywords)
    elif file_ext in [".png", ".jpg", ".jpeg"]:
        found = scan_image(file_path, keywords)
    elif file_ext in [".txt", ".md"]:
        found = scan_txt(file_path, keywords)
    else:
        print(f"Error: Unsupported file type '{file_ext}'.")
    
    return found

def main():
    parser = argparse.ArgumentParser(description="Scan a document for specific keywords or clauses.")
    parser.add_argument("input", help="Path to the input document (PDF, image, txt, or md).")
    parser.add_argument('--keywords', nargs='+', required=True, help='The keywords or phrases to search for.')

    args = parser.parse_args()

    found_keywords = scan(args.input, args.keywords)

    if found_keywords:
        print(f"Found the following keywords in '{args.input}':")
        for keyword in found_keywords:
            print(f"- {keyword}")
    else:
        print(f"No keywords found in '{args.input}'.")

if __name__ == "__main__":
    main()
