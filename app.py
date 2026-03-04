from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# Environment Variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
SECRET = os.environ.get("SECRET")
DEFAULT_CHAT_ID = os.environ.get("CHAT_ID", "-1003602691495") # Better to use env var

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

@app.route("/", methods=["GET"])
def health_check():
    return "Bot is running!", 200

@app.route("/", methods=["POST"])
def webhook():
    try:
        # 1. Get the data
        data = request.get_json(silent=True)
        
        if not data:
            # Fallback for plain text or malformed JSON
            raw_data = request.data.decode("utf-8")
            return jsonify({"error": "Invalid JSON format"}), 400

        # 2. 🔐 Strict secret validation
        if data.get("secret") != SECRET:
            print(f"Unauthorized access attempt with secret: {data.get('secret')}")
            return jsonify({"error": "unauthorized"}), 403

        # 3. Universal Message Handling

        if "text" in data:
            clean_message = data["text"]

        else:
            ticker = data.get("ticker", "Unknown Ticker")
            action = data.get("action", "Alert Triggered")
            price = data.get("price", "N/A")
    
        clean_message = f"<b>🔔 Alert: {ticker}</b>\nAction: {action}\nPrice: {price}"
        
        telegram_payload = {
            "chat_id": DEFAULT_CHAT_ID,
            "text": clean_message,
            "parse_mode": "HTML"
        }

        # 4. Forward to Telegram
        response = requests.post(TELEGRAM_URL, json=telegram_payload, timeout=10)
        return jsonify({"status": "ok", "telegram_response": response.json()})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    # Use the PORT env var provided by Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

