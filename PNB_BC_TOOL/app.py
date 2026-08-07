import os
import logging
import streamlit as st

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from extractor import extract_text
from parser import parse_data
from formatter import generate_word_document as generate_docx


def init_session_state():
    if "extracted_text" not in st.session_state:
        st.session_state.extracted_text = None

    if "parsed_data" not in st.session_state:
        st.session_state.parsed_data = None

    if "docx_path" not in st.session_state:
        st.session_state.docx_path = None


def setup_page_config():
    st.set_page_config(
        page_title="PNB BC Agent Passbook Formatter Pro",
        page_icon="📘",
        layout="wide"
    )


def render_main_dashboard():

    st.title("PNB BC Agent Passbook Formatter Pro")

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"]
    )

    if uploaded_file:

        if st.button("Extract Data"):

            try:
                text = extract_text(uploaded_file)

                st.session_state.extracted_text = text

                data = parse_data(text)

                st.session_state.parsed_data = data

                st.session_state.docx_path = None

            except Exception as e:
                st.error(str(e))

    if st.session_state.parsed_data:

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Extracted Raw Text")

            st.text_area(
                "Raw Text",
                st.session_state.extracted_text,
                height=400
            )

        with col2:

            st.subheader("Parsed Customer Data")

            st.json(st.session_state.parsed_data)

            if st.button("Generate Passbook"):

                try:

                    output_path = generate_docx(
                        st.session_state.parsed_data
                    )

                    st.session_state.docx_path = output_path

                except Exception as e:
                    st.error(str(e))

            if (
                st.session_state.docx_path
                and
                os.path.exists(st.session_state.docx_path)
            ):

                with open(
                    st.session_state.docx_path,
                    "rb"
                ) as f:

                    st.download_button(
                        "Download DOCX",
                        f,
                        "PNB_Passbook.docx"
                    )


def main():

    init_session_state()

    setup_page_config()

    render_main_dashboard()


if __name__ == "__main__":
    main()