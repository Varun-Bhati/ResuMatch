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
    If little or no text is found, use lightweight OCR
    for scanned/image-based PDFs.
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
    # STEP 2: Lightweight OCR
    # -----------------------------------

    try:
        pdf_document = fitz.open(file_path)
        ocr_text = ""

        for page in pdf_document:

            # Slightly higher resolution for better OCR accuracy
            # while keeping processing lighter than 1.5x.
            pix = page.get_pixmap(
                matrix=fitz.Matrix(1.25, 1.25),
                colorspace=fitz.csGRAY
            )

            image = pix.pil_image()

            # PSM 6 works well for a single resume page
            # with multiple text blocks.
            page_text = pytesseract.image_to_string(
                image,
                lang="eng",
                config="--psm 6",
                timeout=15
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