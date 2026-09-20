from pypdf import PdfReader
from docx import Document

import os
import fitz
import pytesseract


# Use the Windows Tesseract path when running locally.
# In Docker/Linux, Tesseract is installed system-wide
# and is already available on PATH.
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )


def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF.

    First, try normal PDF text extraction using pypdf.
    If the PDF contains little or no selectable text,
    automatically use OCR with Tesseract.
    """

    # -----------------------------------
    # STEP 1: Normal PDF text extraction
    # -----------------------------------

    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    # If enough text was extracted, return it normally.
    # This means normal text-based PDFs do NOT need OCR.
    if len(text.strip()) >= 100:
        return text

    # -----------------------------------
    # STEP 2: OCR for scanned/image PDFs
    # -----------------------------------

    try:
        pdf_document = fitz.open(file_path)
        ocr_text = ""

        for page in pdf_document:

            # Render the PDF page as an image.
            # 2.0x gives good OCR quality without being excessive.
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

            # Convert the rendered page into an image.
            image = pix.pil_image()

            # Run Tesseract OCR.
            page_text = pytesseract.image_to_string(
                image,
                lang="eng"
            )

            ocr_text += page_text + "\n"

        pdf_document.close()

        return ocr_text

    except Exception as e:
        print(f"OCR failed: {e}")

        # Return the original extracted text if OCR fails.
        return text


def extract_text_from_docx(file_path):
    document = Document(file_path)

    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text