import requests

# === YOUR TELEGRAM SETTINGS ===
TELEGRAM_TOKEN = "8515005365:AAFdDnUS51Bh8FjgpdRAzfPCqmex8ey9VVM"
TELEGRAM_CHAT_ID = "7688313742"   # ← Your ID (already filled)

def send_telegram_alert(new_bids):
    if not new_bids:
        return

    message = f"🚨 **{len(new_bids)} New Matching Bids Found!**\n\n"
    for bid in new_bids[:5]:
        message += f"**{bid['agency']}**\n"
        message += f"{bid['title']}\n"
        message += f"🔗 {bid['url']}\n\n"
    
    if len(new_bids) > 5:
        message += f"... +{len(new_bids)-5} more"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    
    try:
        requests.post(url, json=payload, timeout=10)
        print("📱 Telegram notification sent successfully!")
    except Exception as e:
        print(f"Telegram send failed: {e}")