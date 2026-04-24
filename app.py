import streamlit as st
import pandas as pd
from database import get_all_bids
from datetime import datetime

# === PAGE CONFIG + PWA ===
st.set_page_config(
    page_title="SafeScan BidWatch",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<link rel="manifest" href="data:application/manifest+json,{
    \\"name\\": \\"SafeScan BidWatch\\",
    \\"short_name\\": \\"SafeScan\\",
    \\"start_url\\": \\"/\\",
    \\"display\\": \\"standalone\\",
    \\"background_color\\": \\"#ffffff\\",
    \\"theme_color\\": \\"#007BFF\\",
    \\"icons\\": [{
        \\"src\\": \\"https://raw.githubusercontent.com/sanchez-cpu/SafeScan-BidWatch/main/SafeScan_Logo.png\\",
        \\"sizes\\": \\"192x192\\",
        \\"type\\": \\"image/png\\"
    }]
}">
""", unsafe_allow_html=True)

# === STYLING ===
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    h1, h2, h3 { color: #1a1a2e; }
    .stButton>button { background-color: #007BFF; color: white; font-weight: 600; border-radius: 8px; }
    .stButton>button:hover { background-color: #0056b3; }
    </style>
""", unsafe_allow_html=True)

# === HEADER ===
st.title("🔍 SafeScan BidWatch")
st.markdown("**Utility
