import streamlit as st
import pandas as pd
from database import get_all_bids
from datetime import datetime

st.set_page_config(page_title="SafeScan BidWatch", page_icon="🔍", layout="wide")

# === HEADER ===
st.title("🔍 SafeScan BidWatch")
st.markdown("**Utility Locating Services** — Florida Procurement Intelligence")

df = get_all_bids()

# === WELCOME + STATS ROW (Like BidHound) ===
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Bids", len(df) if not df.empty else 0, delta="New this week")

with col2:
    locating = len(df[df['keywords_matched'] != ""]) if not df.empty else 0
    st.metric("Locating Matches", locating)

with col3:
    new_this_week = len(df[pd.to_datetime(df['first_seen'], errors='coerce') > pd.Timestamp.now() - pd.Timedelta(days=7)]) if not df.empty else 0
    st.metric("New This Week", new_this_week)

with col4:
    agencies = df['agency'].nunique() if not df.empty else 0
    st.metric("Agencies Tracked", agencies)

st.divider()

# === MAIN CONTENT ===
tab1, tab2 = st.tabs(["📋 All Bids", "🗑️ Manage"])

with tab1:
    if not df.empty:
        search = st.text_input("🔍 Search bids", placeholder="Type to filter...")
        
        if search:
            filtered = df[
                df['title'].str.contains(search, case=False, na=False) | 
                df['keywords_matched'].str.contains(search, case=False, na=False)
            ]
        else:
            filtered = df

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
        st.info("No bids yet. Run the scraper!")

with tab2:
    st.subheader("🗑️ Manage Bids")
    if not df.empty:
        selected = st.multiselect("Select bids to delete", df['id'].tolist(), 
                                  format_func=lambda x: df[df['id']==x]['title'].iloc[0][:70])
        if st.button("🗑️ Delete Selected Bids"):
            if selected:
                import sqlite3
                conn = sqlite3.connect("bids.db")
                conn.execute("DELETE FROM bids WHERE id IN (" + ",".join(["?"]*len(selected)) + ")", selected)
                conn.commit()
                conn.close()
                st.success(f"Deleted {len(selected)} bids!")
                st.rerun()
    else:
        st.info("No bids to manage.")

# === RUN BUTTONS ===
st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("🚀 Run Regular Scraper (All 67 Counties)", type="primary"):
        with st.spinner("Scanning all Florida..."):
            from scraper import run_scraper
            new = run_scraper()
        st.success(f"✅ Found {len(new)} new bids!")
        st.rerun()

with col2:
    if st.button("🔐 Run Premium (Jacksonville–Orlando)", type="secondary"):
        with st.spinner("Premium scanning..."):
            from premium_scraper import run_premium_scraper
            new = run_premium_scraper()
        st.success(f"✅ Found {len(new)} new bids!")
        st.rerun()
