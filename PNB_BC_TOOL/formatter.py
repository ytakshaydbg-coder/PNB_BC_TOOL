import os
import logging
from typing import Dict, Any
from docx import Document

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def replace_text_in_paragraph(paragraph: Any, replacements: Dict[str, str]):

    for run in paragraph.runs:
        for placeholder, value in replacements.items():
            if placeholder in run.text:
                run.text = run.text.replace(
                    placeholder,
                    str(value)
                )

    for placeholder, value in replacements.items():

        if placeholder in paragraph.text:

            full_text = paragraph.text.replace(
                placeholder,
                str(value)
            )

            if paragraph.runs:

                paragraph.runs[0].text = full_text

                for run in paragraph.runs[1:]:
                    run.text = ""


def generate_word_document(
    data: Dict[str, str],
    template_path: str = None,
    output_filename: str = "PNB_Passbook.docx"
) -> str:

    if template_path is None:

        template_path = os.path.join(
            BASE_DIR,
            "template.docx"
        )

    output_dir = os.path.join(
        BASE_DIR,
        "outputs"
    )

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    output_path = os.path.join(
        output_dir,
        output_filename
    )

    replacements = {
        "{{NAME}}": data.get("NAME", ""),
        "{{CIF}}": data.get("CIF", ""),
        "{{ACCOUNT_NO}}": data.get("ACCOUNT_NO", ""),
        "{{AADHAAR}}": data.get("AADHAAR", ""),
        "{{MODE}}": data.get("MODE", ""),
        "{{OPEN_DATE}}": data.get("OPEN_DATE", ""),
        "{{ADDRESS}}": data.get("ADDRESS", ""),
        "{{PIN}}": data.get("PIN", ""),
        "{{NOMINATION}}": data.get("NOMINATION", ""),
        "{{ISSUE_DATE}}": data.get("ISSUE_DATE", "")
    }

    try:

        if not os.path.exists(template_path):

            raise FileNotFoundError(
                f"Template not found: {template_path}"
            )

        doc = Document(template_path)

        for paragraph in doc.paragraphs:

            replace_text_in_paragraph(
                paragraph,
                replacements
            )

        for table in doc.tables:

            for row in table.rows:

                for cell in row.cells:

                    for paragraph in cell.paragraphs:

                        replace_text_in_paragraph(
                            paragraph,
                            replacements
                        )

        doc.save(output_path)

        logger.info(
            f"Generated DOCX: {output_path}"
        )

        return output_path

    except Exception as e:

        logger.error(
            f"DOCX Error: {e}",
            exc_info=True
        )

        raise Exception(
            f"DOCX Generation Failed: {e}"
        )