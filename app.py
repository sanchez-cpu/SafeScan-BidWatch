import streamlit as st
import pandas as pd
from database import get_all_bids

st.set_page_config(page_title="SafeScan BidWatch", page_icon="🔍", layout="wide")

st.title("🔍 SafeScan BidWatch")
st.markdown("**Utility Locating Services** — Florida Procurement Intelligence")

df = get_all_bids()

# === TOP STATS (BidHound Style) ===
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Bids", len(df) if not df.empty else 0)
with col2:
    st.metric("Locating Matches", len(df[df['keywords_matched'] != ""]) if not df.empty else 0)
with col3:
    st.metric("New This Week", len(df[pd.to_datetime(df['first_seen'], errors='coerce') > pd.Timestamp.now() - pd.Timedelta(days=7)]) if not df.empty else 0)
with col4:
    st.metric("Agencies", df['agency'].nunique() if not df.empty else 0)

st.divider()

# === BID CARDS (Modern Look) ===
st.subheader("📋 Recent Bids")

if not df.empty:
    search = st.text_input("🔍 Search", placeholder="Type to filter bids...")
    
    filtered = df
    if search:
        filtered = df[
            df['title'].str.contains(search, case=False, na=False) | 
            df['keywords_matched'].str.contains(search, case=False, na=False)
        ]
    
    # Show as cards (3 per row)
    for i in range(0, len(filtered), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(filtered):
                row = filtered.iloc[i + j]
                with col:
                    with st.container(border=True):
                        st.markdown(f"**{row['title'][:80]}...**")
                        st.caption(f"**{row['agency']}**")
                        if row['keywords_matched']:
                            st.caption(f"🎯 {row['keywords_matched']}")
                        st.link_button("Open Bid →", row['url'])
else:
    st.info("No bids yet. Run the scraper!")

# === RUN BUTTONS ===
st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("🚀 Run Regular Scraper (All 67)", type="primary"):
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
