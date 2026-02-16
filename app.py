from flask import Flask, request
import requests
import os

TOKEN = os.environ.get("TOKEN")

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    
    url = f"https://api.telegram.org/bot8296969716:AAH8HLVUTtwHbk2FBPsSxuNsUl7DE_fN10o/sendMessage"
    r = requests.post(url, json=data)

    print("Telegram response:", r.text)
    return {"status": "ok"}

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=10000)
