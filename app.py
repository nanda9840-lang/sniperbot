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
            return jsonify({"error": "Invalid JSON"}), 400

        if data.get("secret") != SECRET:
            return jsonify({"error": "Unauthorized"}), 403

        # ─────────────────────────────
        # BUILD MESSAGE FIRST
        # ─────────────────────────────

        if "text" in data and data["text"]:
            clean_message = data["text"]
        else:
            ticker = data.get("ticker", "Unknown")
            action = data.get("action", "Alert")
            price = data.get("price", "N/A")

            clean_message = (
                f"<b>🔔 {ticker}</b>\n"
                f"Action: {action}\n"
                f"Price: {price}"
            )

        # ─────────────────────────────
        # DEFINE TELEGRAM PAYLOAD HERE
        # ─────────────────────────────

        telegram_payload = {
            "chat_id": DEFAULT_CHAT_ID,
            "text": clean_message,
            "parse_mode": "HTML"
        }

        response = requests.post(
            TELEGRAM_URL,
            json=telegram_payload,
            timeout=10
        )

        if response.status_code != 200:
            return jsonify({
                "error": "Telegram API failed",
                "details": response.text
            }), 500

        return jsonify({"status": "ok"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN SERVER (Render Compatible)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)




