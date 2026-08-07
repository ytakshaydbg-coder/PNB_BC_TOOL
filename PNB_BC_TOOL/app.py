import os
import logging
import streamlit as st

from extractor import extract_text
from parser import parse_data
from formatter import generate_word_document as generate_docx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def init_session_state():

    if "extracted_text" not in st.session_state:
        st.session_state.extracted_text = None

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


def main():

    setup_page()
    init_session_state()

    st.title("📘 PNB BC Agent Passbook Formatter Pro")

    uploaded_file = st.file_uploader(
        "Upload Passbook PDF",
        type=["pdf"]
    )

    if uploaded_file is not None:

        if st.button("Extract Data"):

            try:

                with st.spinner("Extracting Data..."):

                    text = extract_text(uploaded_file)

                    st.session_state.extracted_text = text

                    parsed = parse_data(text)

                    st.session_state.parsed_data = parsed

                    st.session_state.docx_path = None

                st.success("Data Extracted Successfully")

            except Exception as e:

                st.error(f"Error: {e}")

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

                    with st.spinner("Generating DOCX..."):

                        output_path = generate_docx(
                            st.session_state.parsed_data
                        )

                    if output_path and os.path.exists(output_path):

                        st.session_state.docx_path = output_path

                        st.success(
                            "Passbook Generated Successfully"
                        )

                    else:

                        st.error(
                            "DOCX generation failed."
                        )

                except Exception as e:

                    st.error(f"Generate Error: {e}")

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
                ) as file:

                    st.download_button(
                        label="⬇ Download DOCX",
                        data=file,
                        file_name="PNB_Passbook.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )


if __name__ == "__main__":
    main()
