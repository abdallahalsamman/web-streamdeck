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
body, .webdeck-button {
    transition: background-color 0.3s, color 0.3s;
}

body {
    background-color: #FFFFFF;
    color: #000000;
}

.webdeck-button {
    padding: 5px;
    border: 1px solid black;
    width: 55px;
    height: 55px;
    border-radius: 5px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.special {
    background-color: #4CAF50;
    color: white;
}

/* Dark mode styles */
@media (prefers-color-scheme: dark), .dark-mode {
    body {
        background-color: #121212;
        color: #E0E0E0;
    }
    .webdeck-button {
        background-color: #333333;
        border-color: #444444;
        color: #E0E0E0;
    }
    .special {
        background-color: #4CAF50;
        color: #000000;
    }
}
</style>
<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
</head>
<body>
"""

end = """
<br>
<br>
<span id="fullscreen-btn" class="webdeck-button special">Fullscreen</span>
<!-- <span id="toggle-dark-mode" class="webdeck-button special">Dark Mode</span> -->
<span id="refresh-page" class="webdeck-button special">Refresh</span>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
<script>
$(document).ready(function() {
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    $("span.webdeck-button").each(function() {
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
    /*const toggleDarkMode = () => {
        document.body.classList.toggle('dark-mode');
    };
    document.getElementById('toggle-dark-mode').addEventListener('click', toggleDarkMode);*/
    const refreshPage = () => {
        window.location.reload();
    };
    document.getElementById('refresh-page').addEventListener('click', refreshPage);
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
        threading.Thread(target=lambda: os.system('dotoold &')).start()

        @self.app.route("/")
        def index():
            self.refresh_widgets()
            widget_spans = []
            for link, widget in zip(self.links, self.widgets):
                if widget["text"].endswith(">"):
                    widget_spans.append(widget["text"])
                    continue
                span = "<span id=\"{}\" class=\"webdeck-button\" >{}</span>".format(link, widget["text"])
                widget_spans.append(span)
            widget_html = "\n".join(widget_spans)
            return render_template_string(start + widget_html + end)
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