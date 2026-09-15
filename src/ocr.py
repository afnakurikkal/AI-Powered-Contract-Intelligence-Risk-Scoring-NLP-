import argparse
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path


def extract_text_from_pdf(pdf_path, poppler_path=None, tesseract_path=None):
    """
    Convert PDF pages to images and extract text using Tesseract OCR.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

    pages = convert_from_path(
        pdf_path,
        poppler_path=poppler_path
    )

    extracted_text = []

    for page_number, page in enumerate(pages, start=1):
        text = pytesseract.image_to_string(page)

        extracted_text.append(
            f"\n--- Page {page_number} ---\n{text}"
        )

    return "\n".join(extracted_text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract text from a PDF using OCR"
    )

    parser.add_argument(
        "pdf_path",
        help="Path to the PDF file"
    )

    parser.add_argument(
        "--poppler-path",
        default=None,
        help="Path to Poppler bin folder"
    )

    parser.add_argument(
        "--tesseract-path",
        default=None,
        help="Path to tesseract.exe"
    )

    args = parser.parse_args()

    try:
        text = extract_text_from_pdf(
            args.pdf_path,
            poppler_path=args.poppler_path,
            tesseract_path=args.tesseract_path
        )

        print(text)

    except Exception as error:
        print(f"Error: {error}")