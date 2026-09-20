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

            # Render the page at low resolution in grayscale.
            # This keeps the OCR workload lightweight on Render.
            pix = page.get_pixmap(
                matrix=fitz.Matrix(1.0, 1.0),
                colorspace=fitz.csGRAY
            )

            image = pix.pil_image()

            image_width, image_height = image.size

            # -----------------------------------
            # Overlapping OCR regions
            # -----------------------------------
            #
            # The two regions overlap around the middle
            # of the page. This helps preserve section
            # headings that fall near the split point.
            #

            split_start = int(image_height * 0.40)
            split_end = int(image_height * 0.60)

            top_region = image.crop(
                (0, 0, image_width, split_end)
            )

            bottom_region = image.crop(
                (0, split_start, image_width, image_height)
            )

            # -----------------------------------
            # OCR top region
            # -----------------------------------

            top_text = pytesseract.image_to_string(
                top_region,
                lang="eng",
                config="--psm 6",
                timeout=10
            )

            # -----------------------------------
            # OCR bottom region
            # -----------------------------------

            bottom_text = pytesseract.image_to_string(
                bottom_region,
                lang="eng",
                config="--psm 6",
                timeout=10
            )

            # -----------------------------------
            # Remove duplicate OCR lines
            # -----------------------------------
            #
            # Because the regions overlap, some headings
            # or lines can appear twice. Keep the first
            # occurrence and remove exact duplicate lines.
            #

            combined_text = top_text + "\n" + bottom_text

            seen_lines = set()
            cleaned_lines = []

            for line in combined_text.splitlines():

                normalized_line = " ".join(line.split()).strip()

                if not normalized_line:
                    continue

                if normalized_line.lower() in seen_lines:
                    continue

                seen_lines.add(normalized_line.lower())
                cleaned_lines.append(line.strip())

            ocr_text += "\n".join(cleaned_lines) + "\n"

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