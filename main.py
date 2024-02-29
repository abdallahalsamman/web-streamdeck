from flask import Flask, render_template_string
from flask_socketio import SocketIO
import json
import os
import threading

start = """
<!DOCTYPE html>
<html>
<head>
<title>Soundboard</title>
<style>
.webdeck-button {
    padding: 10px;
    border: 1px solid black;
    width: 75px;
    height: 75px;
    border-radius: 5px;
    cursor: pointer;
    text-align: center;
    word-wrap: break-word;
}
</style>
<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
</head>
<body>
<div style="display: flex; flex-wrap: wrap; gap: 5px;" class="actions-containter">
"""

end = """
</div>
<button id="fullscreen-btn">Toggle Fullscreen</button>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
<script>
$(document).ready(function() {
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    $(".actions-containter *").each(function() {
        if (this.id) {
            this.addEventListener("click", function() {
                socket.emit('run_action', {id: this.id});
            });
        }
    });
    socket.on('connect', function() {
        console.log('Websocket connected!');
    });
    document.getElementById('fullscreen-btn').addEventListener('click', function() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    });
});
</script>
</body>
</html>
"""

class Soundboard:
    def __init__(self):
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app)
        self.widgets = []  # Initialize widgets here
        self.links = []  # It's also a good idea to initialize any other attributes you'll use

        @self.app.route("/")
        def index():
            self.refresh_widgets()
            return render_template_string(start + "\n".join(["<div id=\"{}\" class=\"webdeck-button\" >{}</div>".format(link, widget["text"]) for link, widget in zip(self.links, self.widgets)]) + end)

        @self.socketio.on('run_action')
        def handle_run_action(message):
            link = message['id']
            print(f"Running action for link {link}")
            widget = self.widgets[int(link)]
            threading.Thread(target=lambda: os.system(widget["action"])).start()

    def refresh_widgets(self):
        with open("widgets.json") as f:
            self.widgets = json.load(f)
        self.links = list(range(len(self.widgets)))

if __name__ == "__main__":
    soundboard = Soundboard()
    soundboard.socketio.run(soundboard.app, host="0.0.0.0", port=5000)