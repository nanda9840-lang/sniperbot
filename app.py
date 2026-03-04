from flask import Flask, request, jsonify
import requests
import os
import logging

app = Flask(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENVIRONMENT VARIABLES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
SECRET = os.environ.get("SECRET")
DEFAULT_CHAT_ID = os.environ.get("DEFAULT_CHAT_ID")

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN not set in environment variables")

if not SECRET:
    raise ValueError("❌ SECRET not set in environment variables")

if not DEFAULT_CHAT_ID:
    raise ValueError("❌ CHAT_ID not set in environment variables")

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

logging.basicConfig(level=logging.INFO)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HEALTH CHECK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route("/", methods=["GET"])
def health():
    return "SniperBot Webhook Running 🚀", 200


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# WEBHOOK ENDPOINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json(silent=True)

        if not data:
            logging.warning("⚠ Invalid JSON received")
            return jsonify({"error": "Invalid JSON format"}), 400

        # 🔐 Secret Validation
        if data.get("secret") != SECRET:
            logging.warning("🚨 Unauthorized attempt")
            return jsonify({"error": "Unauthorized"}), 403

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # MESSAGE HANDLING
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━

        if "text" in data and data["text"]:
            clean_message = data["text"]

        else:
            ticker = data.get("ticker", "Unknown")
            action = data.get("action", "Alert Triggered")
            price = data.get("price", "N/A")

            clean_message = (
                f"<b>🔔 Alert: {ticker}</b>\n"
                f"Action: {action}\n"
                f"Price: {price}"
            )

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # SEND TO TELEGRAM
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━

        response = requests.post(
            TELEGRAM_URL,
            json=telegram_payload,
            timeout=10
        )

        if response.status_code != 200:
            logging.error(f"Telegram API Error: {response.text}")
            return jsonify({
                "error": "Telegram API failed",
                "details": response.text
            }), 500

        return jsonify({
            "status": "ok",
            "telegram_response": response.json()
        })

    except Exception as e:
        logging.exception("🔥 Unexpected server error")
        return jsonify({"error": str(e)}), 500


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN SERVER (Render Compatible)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


