from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
SECRET = os.environ.get("SECRET")
DEFAULT_CHAT_ID = "-1003602691495"

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable not set")

if not SECRET:
    raise ValueError("SECRET environment variable not set")

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


@app.route("/", methods=["POST"])
def webhook():

    try:
        raw_data = request.data.decode("utf-8")

        try:
            data = json.loads(raw_data)
        except:
            data = None

        # 🔐 Strict secret validation
        if not isinstance(data, dict) or data.get("secret") != SECRET:
            return jsonify({"error": "unauthorized"}), 403

        # If JSON already formatted for Telegram
        if "chat_id" in data and "text" in data:
            telegram_payload = data
        else:
            telegram_payload = {
                "chat_id": DEFAULT_CHAT_ID,
                "text": json.dumps(data, indent=2),
                "parse_mode": "HTML"
            }

        response = requests.post(TELEGRAM_URL, json=telegram_payload, timeout=10)

        return jsonify({
            "status": "ok",
            "telegram_response": response.json()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run()
