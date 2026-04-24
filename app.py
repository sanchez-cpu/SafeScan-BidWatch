import streamlit as st
import pandas as pd
from database import get_all_bids
from datetime import datetime

# === PAGE CONFIG ===
st.set_page_config(
    page_title="SafeScan BidWatch",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === PWA SUPPORT ===
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

# === CUSTOM STYLING (Matches SafeScanutilities.com) ===
st.markdown("""
    <style>
    .main {
        background-color: #ffffff;
    }
    h1, h2, h3 {
        color: #1a1a2e;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    .stButton>button {
        background-color: #007BFF;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 10px 24px;
    }
    .stButton>button:hover {
        background-color: #0056b3;
    }
    .stMetric {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# === HEADER (Matches your website vibe) ===
st.title("🔍 SafeScan BidWatch")
st.markdown("""
**Utility Locating Services** — Florida Procurement Intelligence  
*Scan Safe, Build Confident*
""")

df = get_all_bids()

# === SIDEBAR ===
st.sidebar.header("🔍 Filters")
search = st.sidebar.text_input("Search Title or Keywords", placeholder="locating, 96291, 811...")

if not df.empty and search:
    filtered = df[
        df['title'].str.contains(search, case=False, na=False) | 
        df['keywords_matched'].str.contains(search, case=False, na=False)
    ]
else:
    filtered = df

# === TABS ===
tab1, tab2, tab3 = st.tabs(["📋 All Bids", "🗑️ Manage Bids", "📊 Stats"])

with tab1:
    if not filtered.empty:
        st.dataframe(
            filtered[['title', 'agency', 'url', 'first_seen', 'keywords_matched']],
            use_container_width=True,
            column_config={
                "url": st.column_config.LinkColumn("Open Bid", display_text="Open →"),
                "first_seen": st.column_config.DatetimeColumn("First Seen"),
            },
            hide_index=True
        )
        st.download_button("📥 Export CSV", filtered.to_csv(index=False), "safescan_bids.csv")
    else:
        st.info("No bids found. Run the scraper.")

with tab2:
    st.subheader("🗑️ Remove Unwanted Bids")
    if not df.empty:
        selected_ids = st.multiselect(
            "Select bids to permanently delete",
            options=df['id'].tolist(),
            format_func=lambda x: df[df['id']==x]['title'].iloc[0][:80] + "..."
        )
        
        if st.button("🗑️ Delete Selected Bids"):
            if selected_ids:
                import sqlite3
                conn = sqlite3.connect("bids.db")
                conn.execute("DELETE FROM bids WHERE id IN (" + ",".join(["?"]*len(selected_ids)) + ")", selected_ids)
                conn.commit()
                conn.close()
                st.success(f"Deleted {len(selected_ids)} bids!")
                st.rerun()
            else:
                st.warning("No bids selected.")
        
        if st.button("⚠️ Clear ALL Bids (Dangerous)"):
            if st.checkbox("I understand this deletes everything"):
                import sqlite3
                conn = sqlite3.connect("bids.db")
                conn.execute("DELETE FROM bids")
                conn.commit()
                conn.close()
                st.success("All bids cleared!")
                st.rerun()
    else:
        st.info("No bids to manage.")

with tab3:
    st.subheader("📊 Statistics")
    if not df.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Bids", len(df))
        c2.metric("Locating Matches", len(df[df['keywords_matched'] != ""]))
        c3.metric("New This Week", len(df[pd.to_datetime(df['first_seen'], errors='coerce') > pd.Timestamp.now() - pd.Timedelta(days=7)]))
        c4.metric("Agencies Tracked", df['agency'].nunique())
    else:
        st.info("No data yet.")

# === RUN BUTTONS ===
col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Run Regular Scraper (All 67 Counties)", type="primary"):
        with st.spinner("Scanning all Florida counties..."):
            from scraper import run_scraper
            new_bids = run_scraper()
        st.success(f"✅ Regular scan done! Found {len(new_bids)} new bids.")
        st.rerun()

with col2:
    if st.button("🔐 Run Premium Scraper (Jacksonville–Orlando)", type="secondary"):
        with
