import streamlit as st
import pandas as pd
from database import get_all_bids
from datetime import datetime

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

st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    h1, h2, h3 { color: #1a1a2e; }
    .stButton>button { background-color: #007BFF; color: white; font-weight: 600; border-radius: 8px; }
    .stButton>button:hover { background-color: #0056b3; }
    </style>
""", unsafe_allow_html=True)

st.title("🔍 SafeScan BidWatch")
st.markdown("**Utility Locating Services** — Florida Procurement Intelligence<br>*Scan Safe, Build Confident*")

df = get_all_bids()

st.sidebar.header("🔍 Filters")
search = st.sidebar.text_input("Search", placeholder="locating, 96291, 811...")

if not df.empty and search:
    filtered = df[
        df['title'].str.contains(search, case=False, na=False) | 
        df['keywords_matched'].str.contains(search, case=False, na=False)
    ]
else:
    filtered = df

tab1, tab2, tab3 = st.tabs(["📋 All Bids", "🗑️ Manage Bids", "📊 Stats"])

with tab1:
    if not filtered.empty:
        st.dataframe(
            filtered[['title', 'agency', 'url', 'first_seen', 'keywords_matched']],
            use_container_width=True,
            column_config={
                "url": st.column_config.LinkColumn("Open →"),
                "first_seen": st.column_config.DatetimeColumn("First Seen"),
            },
            hide_index=True
        )
        st.download_button("📥 Export CSV", filtered.to_csv(index=False), "safescan_bids.csv")
    else:
        st.info("No bids found.")

with tab2:
    st.subheader("🗑️ Remove Bids")
    if not df.empty:
        selected = st.multiselect("Select bids to delete", df['id'].tolist(), 
                                  format_func=lambda x: df[df['id']==x]['title'].iloc[0][:70])
        if st.button("🗑️ Delete Selected"):
            if selected:
                import sqlite3
                conn = sqlite3.connect("bids.db")
                conn.execute("DELETE FROM bids WHERE id IN (" + ",".join(["?"]*len(selected)) + ")", selected)
                conn.commit()
                conn.close()
                st.success(f"Deleted {len(selected)} bids!")
                st.rerun()
        if st.button("⚠️ Clear ALL"):
            if st.checkbox("Confirm delete everything"):
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
        c4.metric("Agencies", df['agency'].nunique())
    else:
        st.info("No data yet.")

col1, col2 = st.columns(2)
with col1:
    if st.button("🚀 Run Regular Scraper (All 67)", type="primary"):
        with st.spinner("Scanning..."):
            from scraper import run_scraper
            new = run_scraper()
        st.success(f"Found {len(new)} new bids!")
        st.rerun()

with col2:
    if st.button("🔐 Run Premium (Jacksonville–Orlando)", type="secondary"):
        with st.spinner("Premium scanning..."):
            from premium_scraper import run_premium_scraper
            new = run_premium_scraper()
        st.success(f"Found {len(new)} new bids!")
        st.rerun()
