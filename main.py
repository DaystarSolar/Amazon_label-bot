from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "✅ Replit backend is live"

@app.route("/run", methods=["POST"])
def run_script():
    try:
        result = subprocess.run(
            ["python3", "download_label.py"],
            check=True,
            capture_output=True
        )
        return "✅ Label downloaded and emailed!"
    except subprocess.CalledProcessError as e:
        return f"❌ Script failed:\n{e.stderr.decode()}"

app.run(host="0.0.0.0", port=3000)
