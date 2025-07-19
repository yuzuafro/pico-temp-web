from flask import Flask, jsonify, render_template
from flask_cors import CORS
import threading, asyncio
from ble_sensor_interface import BleSensorInterface

ble = BleSensorInterface()
app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/temperature")
def get_temperature():
    if ble.temperature is None:
        return jsonify({"error": "No data", "connected": ble.connected}), 404
    return jsonify({"temperature": ble.temperature, "connected": ble.connected})

@app.route("/connect", methods=["POST"])
def connect():
    if not ble.connected:
        def run_ble():
            loop = asyncio.new_event_loop()
            ble.set_loop(loop)
            asyncio.set_event_loop(loop)
            loop.run_until_complete(ble.read_loop())

        threading.Thread(target=run_ble, daemon=True).start()
        return jsonify({"message": "接続開始", "connected": True})
    return jsonify({"message": "すでに接続中です", "connected": True})

@app.route("/disconnect", methods=["POST"])
def disconnect():
    if ble.connected and ble.loop:
        future = asyncio.run_coroutine_threadsafe(ble.disconnect(), ble.loop)
        future.result()
        return jsonify({"message": "切断完了", "connected": False})
    return jsonify({"message": "すでに切断済み", "connected": False})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)