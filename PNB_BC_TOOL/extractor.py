import fitz  # PyMuPDF
import logging
from typing import BinaryIO

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


def extract_text(pdf_file: BinaryIO) -> str:
    """
    Extract all text from a Computer Generated PDF.

    Args:
        pdf_file: Uploaded PDF file (Streamlit UploadedFile)

    Returns:
        str: Extracted text
    """

    try:
        pdf_bytes = pdf_file.read()

        document = fitz.open(stream=pdf_bytes, filetype="pdf")

        extracted_text = ""

        for page in document:
            extracted_text += page.get_text("text")
            extracted_text += "\n"

        document.close()

        logger.info("PDF text extracted successfully.")

        return extracted_text.strip()

    except Exception as e:
        logger.exception("PDF Extraction Failed")
        raise Exception(f"Unable to extract PDF text.\n{e}")