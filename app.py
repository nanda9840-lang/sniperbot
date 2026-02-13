from flask import Flask, request
import requests
import os

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    symbol = data.get("symbol")
    action = data.get("action")
    entry  = data.get("entry")
    tp1    = data.get("tp1")
    tp2    = data.get("tp2")
    tp3    = data.get("tp3")
    sl     = data.get("sl")

    message = f"""
🎯 <b>Universal Adaptive Sniper PRO</b>

<b>Symbol:</b> {symbol}
<b>Action:</b> {action}

🎯 Entry: {entry}
✅ TP1: {tp1}
✅ TP2: {tp2}
✅ TP3: {tp3}
🛑 SL: {sl}
"""

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    requests.post(url, json=payload)

    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)