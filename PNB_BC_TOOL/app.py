import os
import logging
from datetime import datetime
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

def load_css():
    st.markdown("""
    <style>
    /* ====================================================
       THEME & VARIABLES
       ==================================================== */
    :root {
        --bg-color: #050B14;
        --card-bg: #0D1424;
        --border-color: rgba(255, 255, 255, 0.08);
        --primary-accent: #FF5A5F; /* Reddish Orange from screenshot */
        --text-white: #FFFFFF;
        --text-secondary: #9CA3AF;
        --success-green: #10B981;
    }

    /* ====================================================
       GLOBAL OVERRIDES
       ==================================================== */
    [data-testid="stAppViewContainer"], .stApp {
        background-color: var(--bg-color) !important;
        color: var(--text-white) !important;
    }

    [data-testid="stSidebar"] {
        background-color: #03060C !important;
        border-right: 1px solid var(--border-color);
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    h1, h2, h3, h4, h5, h6, p, span, div {
        color: var(--text-white);
    }

    p {
        color: var(--text-secondary);
    }

    hr {
        border-color: var(--border-color) !important;
        margin: 2rem 0;
    }

    /* ====================================================
       SIDEBAR STYLING
       ==================================================== */
    .sidebar-logo {
        font-size: 1.4rem;
        font-weight: 800;
        margin-bottom: 2rem;
        color: var(--text-white);
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .sidebar-menu {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .sidebar-menu li {
        padding: 10px 16px;
        margin-bottom: 8px;
        border-radius: 6px;
        cursor: pointer;
        color: var(--text-secondary);
        font-weight: 500;
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: all 0.2s ease;
    }
    
    .sidebar-menu li.active {
        background: rgba(255, 255, 255, 0.03);
        color: var(--primary-accent);
        border-left: 3px solid var(--primary-accent);
    }

    /* ====================================================
       HERO SECTION
       ==================================================== */
    .hero-container {
        text-align: center;
        padding: 2rem 1rem 3rem 1rem;
    }
    
    .glow-logo {
        width: 70px;
        height: 70px;
        background: #FF8C00;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        box-shadow: 0 0 30px rgba(255, 140, 0, 0.4);
        margin-bottom: 1.5rem;
        border: 3px solid #111;
    }

    .hero-title {
        font-size: 2.75rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.8rem !important;
        color: var(--text-white);
    }

    .hero-subtitle {
        font-size: 0.9rem !important;
        color: var(--primary-accent) !important;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    /* ====================================================
       CARDS & CONTAINERS
       ==================================================== */
    .glass-card {
        background: var(--card-bg);
        border: 1px dashed var(--border-color);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 1.5rem;
    }

    /* Metric Cards */
    .metric-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        position: relative;
        overflow: hidden;
        height: 100%;
        transition: all 0.3s ease;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #FF8C00, transparent);
        opacity: 0.8;
    }

    .metric-card .icon {
        font-size: 2rem;
        margin-bottom: 12px;
    }

    .metric-card .label {
        color: var(--text-secondary);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
    }

    .metric-card .value {
        color: var(--text-white);
        font-size: 1.15rem;
        font-weight: 800;
        margin-top: 8px;
        word-wrap: break-word;
    }

    /* ====================================================
       FIX FOR TEXT AREA (TERMINAL)
       ==================================================== */
    /* Target strictly the inner textarea element to prevent white-on-white */
    div[data-baseweb="base-input"] > textarea,
    .stTextArea textarea {
        background-color: #03060C !important;
        color: #10B981 !important; /* Terminal Green */
        -webkit-text-fill-color: #10B981 !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 0.9rem !important;
        padding: 15px !important;
    }
    
    /* Ensure wrapper background matches */
    div[data-baseweb="base-input"] {
        background-color: #03060C !important;
        border: none !important;
    }

    /* Focus state */
    div[data-baseweb="base-input"]:focus-within {
        border-color: var(--primary-accent) !important;
        box-shadow: 0 0 0 1px var(--primary-accent) !important;
    }

    /* ====================================================
       COMPONENTS (Buttons, Uploader)
       ==================================================== */
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: #F8F9FA;
        border: 1px dashed #D1D5DB;
        border-radius: 8px;
        padding: 16px;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] > div > span {
        color: #111 !important;
        font-weight: 600;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] > div > small {
        color: #666 !important;
    }

    /* Primary Buttons */
    [data-testid="baseButton-primary"] {
        background: var(--primary-accent) !important;
        border: none !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        height: 46px;
        transition: all 0.2s ease !important;
    }
    [data-testid="baseButton-primary"]:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }

    /* ====================================================
       TABLE STYLING
       ==================================================== */
    .premium-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;
        background: transparent;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid var(--border-color);
    }
    
    .premium-table th, .premium-table td {
        padding: 16px;
        text-align: left;
        border-bottom: 1px solid var(--border-color);
    }
    
    .premium-table th {
        color: #FF8C00;
        text-transform: uppercase;
        font-weight: 800;
        letter-spacing: 0.5px;
        font-size: 0.8rem;
    }
    
    .premium-table td {
        color: var(--text-white);
        font-weight: 600;
    }
    
    .premium-table tr:last-child td {
        border-bottom: none;
    }

    /* ====================================================
       ALERTS & FOOTER
       ==================================================== */
    .success-box {
        background: #022C22;
        border: 1px solid #047857;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    .success-box h3 {
        color: var(--success-green) !important;
        margin: 0 0 8px 0;
        font-size: 1.4rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }
    
    .success-box p {
        margin: 0;
        font-size: 0.95rem;
        color: #A7F3D0;
    }

    .footer {
        text-align: center;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid var(--border-color);
        color: var(--text-secondary);
        font-size: 0.85rem;
    }
    </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <span style="background: white; border-radius: 4px; padding: 2px 6px; color: black;">⬜</span>
            PNB BC Tool
        </div>
        
        <ul class="sidebar-menu">
            <li class="active">🏠 Home</li>
            <li>📜 History</li>
            <li>ℹ️ About</li>
        </ul>
        """, unsafe_allow_html=True)

def render_hero():
    st.markdown("""
    <div class="hero-container">
        <div class="glow-logo">🏢</div>
        <h1 class="hero-title">Passbook Formatter Pro</h1>
        <div class="hero-subtitle">PDF ➜ AUTO EXTRACT ➜ AUTO FILL ➜ DOCX DOWNLOAD</div>
    </div>
    """, unsafe_allow_html=True)

def render_features():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin-bottom: 30px;'>Why Use PNB BC Tool?</h3>", unsafe_allow_html=True)
    
    cols = st.columns(5)
    features = [
        ("🔒", "100% Secure", "Bank-grade privacy"),
        ("⚡", "Fast & Accurate", "AI-powered extraction"),
        ("📝", "Auto Formatting", "Ready-to-print docs"),
        ("⏳", "Time Saving", "Process in seconds"),
        ("🤝", "BC Friendly", "Designed for agents")
    ]
    
    for i, (icon, title, desc) in enumerate(features):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card" style="padding: 16px;">
                <div style="font-size: 1.5rem; margin-bottom: 8px;">{icon}</div>
                <div style="color: #FF8C00; font-weight: 800; font-size: 0.85rem; margin-bottom: 4px;">{title}</div>
                <div style="color: #9CA3AF; font-size: 0.75rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

def setup_page():
    st.set_page_config(
        page_title="PNB BC Agent Passbook Formatter Pro",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    load_css()

def render_dashboard():
    render_sidebar()
    render_hero()

    # --- UPLOAD SECTION ---
    col_icon, col_text = st.columns([1, 20])
    with col_icon:
        st.markdown("<h2 style='color:white; margin:0;'>📄</h2>", unsafe_allow_html=True)
    with col_text:
        st.markdown("<h3 style='margin:0; padding-top:4px;'>Upload Passbook PDF</h3>", unsafe_allow_html=True)
        st.markdown("<p style='margin:0; margin-bottom:16px; font-size:0.9rem;'>Upload customer passbook PDF to extract details automatically.</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file:
        if st.button("🚀 Extract Data", type="primary", use_container_width=True):
            with st.spinner("Extracting and Parsing Details..."):
                try:
                    text = extract_text(uploaded_file)
                    parsed = parse_data(text)
                    
                    # --- AUTO DATE DETECTION INJECTION ---
                    # Add current real date as ISSUE_DATE if you need it automatically
                    current_date = datetime.now().strftime("%d-%m-%Y")
                    parsed["ISSUE_DATE"] = current_date
                    
                    st.session_state.extracted_text = text
                    st.session_state.parsed_data = parsed
                    st.session_state.docx_path = None
                    
                except Exception as e:
                    st.error(f"❌ Extraction Error: {str(e)}")

    # --- RESULTS SECTION ---
    if st.session_state.parsed_data:
        data = st.session_state.parsed_data
        
        # 1. CUSTOMER INFO CARDS
        st.markdown("<h3 style='margin-top: 40px; margin-bottom: 20px;'>Customer Overview</h3>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        
        metrics = [
            ("👤", "CUSTOMER NAME", data.get("NAME", data.get("Name", "Not Found"))),
            ("🔢", "CIF NUMBER", data.get("CIF", "Not Found")),
            ("🏦", "ACCOUNT NUMBER", data.get("ACCOUNT_NO", data.get("Account Number", "Not Found"))),
            ("📅", "OPEN DATE", data.get("OPEN_DATE", data.get("Open Date", "Not Found")))
        ]
        
        for col, (icon, label, val) in zip([c1, c2, c3, c4], metrics):
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="icon">{icon}</div>
                    <div class="label">{label}</div>
                    <div class="value">{val}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)

        # 2. MAIN CONTENT (TWO COLUMNS)
        col_left, col_right = st.columns([1, 1], gap="large")

        with col_left:
            st.markdown("<h4><span style='color:#FF8C00;'>Terminal</span> // Raw Extracted Text</h4>", unsafe_allow_html=True)
            # The CSS above strictly targets this text area to fix the white-on-white bug
            st.text_area(
                "Terminal Output",
                st.session_state.extracted_text,
                height=550,
                label_visibility="collapsed",
                key="terminal_output_area"
            )

        with col_right:
            st.markdown("<h4><span style='color:#FF8C00;'>Database</span> // Parsed Customer Data</h4>", unsafe_allow_html=True)
            
            # Keys aligned with the provided screenshot
            keys_to_display = ["CIF", "PIN", "NAME", "ACCOUNT_NO", "AADHAAR", "ADDRESS", "FATHER_NAME", "MODE", "OPEN_DATE", "ISSUE_DATE"]
            
            table_html = "<table class='premium-table'><tr><th>Attribute</th><th>Parsed Value</th></tr>"
            
            # Prioritized display keys
            for key in keys_to_display:
                val = data.get(key, data.get(key.title(), data.get(key.replace("_", " ").title(), None)))
                if val is not None:
                    table_html += f"<tr><td>{key}</td><td>{val}</td></tr>"
                    
            # Add any leftover keys safely
            for key, val in data.items():
                if key.upper() not in keys_to_display and key.replace(" ", "_").upper() not in keys_to_display:
                    table_html += f"<tr><td>{key.upper()}</td><td>{val if val else '—'}</td></tr>"
                    
            table_html += "</table>"
            st.markdown(table_html, unsafe_allow_html=True)

        st.markdown("<br><hr><br>", unsafe_allow_html=True)

        # 3. GENERATE PASSBOOK SECTION
        st.markdown("<h3>Generate Final Passbook 🔗</h3>", unsafe_allow_html=True)
        st.markdown("<p style='margin-bottom:20px;'>Create a perfectly formatted, ready-to-print DOCX file using the extracted customer data above.</p>", unsafe_allow_html=True)
        
        # Wrapping button in a card mimicking the third screenshot layout
        st.markdown("<div class='glass-card' style='padding: 30px;'>", unsafe_allow_html=True)
        
        if not st.session_state.docx_path:
            _, btn_col, _ = st.columns([1, 2, 1])
            with btn_col:
                if st.button("📄 Generate Passbook DOCX", type="primary", use_container_width=True):
                    with st.spinner("Compiling DOCX format..."):
                        try:
                            output_path = generate_word_document(
                                data=st.session_state.parsed_data,
                                output_filename="PNB_Passbook.docx"
                            )
                            if output_path and os.path.exists(output_path):
                                st.session_state.docx_path = output_path
                                st.rerun() # Rerun to show success state immediately
                            else:
                                st.error("❌ DOCX generation failed. File not found.")
                        except Exception as e:
                            st.error(f"❌ Generation Error: {str(e)}")

        # 4. SUCCESS SECTION (Replaces Generate button if successful)
        if st.session_state.docx_path and os.path.exists(st.session_state.docx_path):
            st.markdown("""
            <div class='success-box'>
                <h3>✅ DOCX Generated Successfully</h3>
                <p>Your passbook document is ready for download and printing.</p>
            </div>
            """, unsafe_allow_html=True)
            
            with open(st.session_state.docx_path, "rb") as f:
                _, dl_col, _ = st.columns([1, 2, 1])
                with dl_col:
                    st.download_button(
                        label="⬇ Download Final DOCX",
                        data=f,
                        file_name="PNB_Passbook.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                        type="primary"
                    )
                    
        st.markdown("</div>", unsafe_allow_html=True)

    # --- FEATURES SECTION ---
    render_features()

    # --- FOOTER ---
    st.markdown("""
    <div class="footer">
        © 2026 PNB BC Tool &nbsp;|&nbsp; Built with <span style="color: #ef4444;">❤️</span> by Akshu
    </div>
    """, unsafe_allow_html=True)

def main():
    init_session_state()
    setup_page()
    render_dashboard()

if __name__ == "__main__":
    main()