from pypdf import PdfReader
from docx import Document

import os
import fitz
import pytesseract


# Use the Windows Tesseract path when running locally.
# In Docker/Linux, Tesseract is installed system-wide
# and is available on PATH.
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )


def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF.

    First, try normal PDF text extraction.
    If little or no text is found, use OCR for scanned PDFs.
    """

    # -----------------------------------
    # STEP 1: Normal PDF text extraction
    # -----------------------------------

    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    if len(text.strip()) >= 100:
        return text

    # -----------------------------------
    # STEP 2: OCR for scanned/image PDFs
    # -----------------------------------

    try:
        pdf_document = fitz.open(file_path)
        ocr_text = ""

        for page in pdf_document:

            # Render at 1.5x instead of 2x.
            # This reduces memory usage on small servers.
            pix = page.get_pixmap(
                matrix=fitz.Matrix(1.5, 1.5)
            )

            image = pix.pil_image()

            # Give each Tesseract page operation a maximum
            # of 20 seconds.
            page_text = pytesseract.image_to_string(
                image,
                lang="eng",
                timeout=20
            )

            ocr_text += page_text + "\n"

        pdf_document.close()

        return ocr_text

    except Exception as e:
        print(f"OCR failed: {e}")
        return text


def extract_text_from_docx(file_path):
    document = Document(file_path)

    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text