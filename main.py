from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "✅ Replit backend is live"

@app.route("/run", methods=["POST"])
def run_script():
    try:
        subprocess.run(["python3", "download_label.py"], check=True)
        return "✅ Label downloaded and emailed!"
    except Exception as e:
        return f"❌ Error: {str(e)}"

app.run(host="0.0.0.0", port=3000)
	