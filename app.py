import streamlit as st
import pandas as pd
from database import get_all_bids
from datetime import datetime

st.set_page_config(page_title="SafeScan BidWatch", layout="wide", page_icon="🔍")

# SafeScan Color Scheme
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    h1, h2 { color: #000000; }
    .stButton>button { background-color: #facc15; color: black; font-weight: bold; }
    .stButton>button:hover { background-color: #eab308; }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("🔍 SafeScan BidWatch")
st.caption("**Utility Locating Services** — Florida Government Bid Monitor")

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 All Bids", "🔥 New & Matching", "📊 Statistics"])

df = get_all_bids()

# Filters (shared)
search = st.sidebar.text_input("🔍 Search", placeholder="locating, 96291, 811, utility locate...")
if not df.empty and search:
    df_filtered = df[
        df['title'].str.contains(search, case=False, na=False) | 
        df['keywords_matched'].str.contains(search, case=False, na=False)
    ]
else:
    df_filtered = df

with tab1:
    st.subheader("All Tracked Bids")
    if not df.empty:
        st.dataframe(
            df[['title', 'agency', 'url', 'first_seen', 'keywords_matched']],
            use_container_width=True,
            column_config={
                "url": st.column_config.LinkColumn("View Bid", display_text="Open →"),
                "first_seen": st.column_config.DatetimeColumn("First Seen"),
            },
            hide_index=True
        )
        st.download_button("📥 Export All Bids", df.to_csv(index=False), "all_bids.csv")
    else:
        st.info("No bids yet.")

with tab2:
    st.subheader("🔥 New & Locating Matches")
    if not df.empty:
        recent = df[pd.to_datetime(df['first_seen'], errors='coerce') > pd.Timestamp.now() - pd.Timedelta(days=7)]
        matches = df[df['keywords_matched'] != ""]
        
        st.dataframe(
            matches[['title', 'agency', 'url', 'first_seen', 'keywords_matched']],
            use_container_width=True,
            column_config={"url": st.column_config.LinkColumn("Open →")},
            hide_index=True
        )
    else:
        st.info("Run the scraper to see matches.")

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

# Run Button
if st.button("🚀 Run Scraper Now", type="primary", use_container_width=True):
    with st.spinner("Scanning Florida counties for utility locating bids..."):
        from scraper import run_scraper
        from notifier import send_telegram_alert
        new_bids = run_scraper()
        if new_bids:
            send_telegram_alert(new_bids)
    st.success(f"✅ Scan complete! Found {len(new_bids)} new bids.")
    st.rerun()