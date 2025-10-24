# ai_app/utils.py

import fitz  # PyMuPDF
from io import BytesIO


def extract_text_from_pdf(pdf_file) -> str:
    """
    Extracts all text from an uploaded PDF file using PyMuPDF (fitz).

    Args:
        pdf_file: A Django UploadedFile object.

    Returns:
        The concatenated text content of the PDF.
    """
    text = ""
    try:
        # Read file content into a memory stream
        pdf_data = pdf_file.read()
        pdf_stream = BytesIO(pdf_data)

        # Open PDF from memory stream
        doc = fitz.open(stream=pdf_stream, filetype="pdf")

        for page in doc:
            text += page.get_text()

        return text

    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""