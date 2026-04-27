from flask import Flask, render_template
from flask_socketio import SocketIO
from core.processor import Processor
import threading

app = Flask(__name__, template_folder="ui")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

def emit(data):
    socketio.emit("transcript", data)

processor = Processor(emit)

started = False

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("connect")
def on_connect():
    global started
    print("Client connected")

    if not started:
        print("Starting processor...")
        threading.Thread(target=processor.run, daemon=True).start()
        started = True

if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000)