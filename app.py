from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

SECRET = "mysecretkey"

TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
DEFAULT_CHAT_ID = "-1003602691495"
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


@app.route("/", methods=["POST"])
def webhook():

    try:
        raw_data = request.data.decode("utf-8")

        # Try parse JSON
        try:
            data = json.loads(raw_data)
        except:
            data = None

        # 🔐 Secret validation (if JSON contains secret)
        if isinstance(data, dict) and "secret" in data:
            if data.get("secret") != SECRET:
                return jsonify({"error": "unauthorized"}), 403

        # If JSON already formatted for Telegram
        if isinstance(data, dict) and "chat_id" in data and "text" in data:
            telegram_payload = data

        # If JSON but not Telegram format
        elif isinstance(data, dict):
            telegram_payload = {
                "chat_id": DEFAULT_CHAT_ID,
                "text": json.dumps(data, indent=2),
                "parse_mode": "HTML"
            }

        # If plain text
        else:
            telegram_payload = {
                "chat_id": DEFAULT_CHAT_ID,
                "text": raw_data,
                "parse_mode": "HTML"
            }

        response = requests.post(TELEGRAM_URL, json=telegram_payload)

        return jsonify({
            "status": "ok",
            "telegram_response": response.json()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run()
