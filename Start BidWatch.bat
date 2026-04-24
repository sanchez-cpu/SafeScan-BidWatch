@echo off
title 🚀 BidWatch - Florida Bid Monitor
cd /d "%~dp0"
echo Starting BidWatch... (Close this window to stop)
python -m streamlit run app.py