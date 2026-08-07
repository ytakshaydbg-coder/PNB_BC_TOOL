import os
import logging
import streamlit as st

from extractor import extract_text
from parser import parse_data
from formatter import generate_word_document

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def init_session_state():
    if "extracted_text" not in st.session_state:
        st.session_state.extracted_text = ""

    if "parsed_data" not in st.session_state:
        st.session_state.parsed_data = None

    if "docx_path" not in st.session_state:
        st.session_state.docx_path = None


def setup_page():
    st.set_page_config(
        page_title="PNB BC Agent Passbook Formatter Pro",
        page_icon="📘",
        layout="wide"
    )


def render_dashboard():

    st.title("📘 PNB BC Agent Passbook Formatter Pro")

    uploaded_file = st.file_uploader(
        "Upload Passbook PDF",
        type=["pdf"]
    )

    if uploaded_file:

        if st.button("Extract Data"):

            try:

                text = extract_text(uploaded_file)

                st.session_state.extracted_text = text

                st.session_state.parsed_data = parse_data(text)

                st.session_state.docx_path = None

                st.success("✅ Data Extracted Successfully")

            except Exception as e:
                st.error(f"❌ Extraction Error: {str(e)}")

    if st.session_state.parsed_data:

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Raw Extracted Text")

            st.text_area(
                "Text",
                st.session_state.extracted_text,
                height=450
            )

        with col2:

            st.subheader("Parsed Customer Data")

            st.json(st.session_state.parsed_data)

            if st.button("Generate Passbook"):

                try:

                    st.info("Generating DOCX...")

                    BASE_DIR = os.path.dirname(
                        os.path.abspath(__file__)
                    )

                    TEMPLATE_PATH = os.path.join(
                        BASE_DIR,
                        "template.docx"
                    )

                    output_path = generate_word_document(
                        st.session_state.parsed_data,
                        template_path=TEMPLATE_PATH,
                        output_filename="PNB_Passbook.docx"
                    )

                    st.write("Generated File:", output_path)

                    if output_path and os.path.exists(output_path):

                        st.session_state.docx_path = output_path

                        st.success(
                            "✅ DOCX Generated Successfully"
                        )

                    else:

                        st.error(
                            "❌ DOCX generation failed."
                        )

                except Exception as e:

                    st.error(
                        f"❌ Generation Error: {str(e)}"
                    )

            if (
                st.session_state.docx_path
                and
                os.path.exists(
                    st.session_state.docx_path
                )
            ):

                with open(
                    st.session_state.docx_path,
                    "rb"
                ) as f:

                    st.download_button(
                        label="⬇ Download DOCX",
                        data=f,
                        file_name="PNB_Passbook.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )


def main():
    init_session_state()
    setup_page()
    render_dashboard()


if __name__ == "__main__":
    main()