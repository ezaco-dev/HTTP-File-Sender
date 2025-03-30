import os
import socket
from flask import Flask, request, send_from_directory, render_template_string
import qrcode

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

LOCAL_IP = get_local_ip()

# Generate QR code for server URL
qr = qrcode.make(f"http://{LOCAL_IP}:5000")
qr_path = os.path.join("static", "server_qr.png")
os.makedirs("static", exist_ok=True)
qr.save(qr_path)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HTTP File Sender - LWS25</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #121212;
            color: #fff;
            text-align: center;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: auto;
            background: #1e1e1e;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 0px 10px rgba(255, 255, 255, 0.1);
        }
        h1, h2 { color: #00ffcc; }
        .qr-container img { width: 150px; margin-top: 10px; }
        form { margin-top: 20px; }
        input[type="file"] {
            background: #333; color: white; border: none;
            padding: 10px; border-radius: 5px;
        }
        button {
            background: #00ffcc; color: black; border: none;
            padding: 10px 15px; border-radius: 5px; cursor: pointer;
            transition: 0.3s;
        }
        button:hover { background: #008f80; }
        ul { list-style: none; padding: 0; }
        li {
            background: #333; margin: 5px 0;
            padding: 10px; border-radius: 7px; display: flex; justify-content: center; align-items: center; gap: 8px
        }
        a { color: #00ffcc; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>HTTP File Sender</h1>
        <p>Share files over the network easily.</p>
        
        <div class="qr-container">
            <img src="{{ url_for('static', filename='server_qr.png') }}" alt="QR Code Server">
            <p>Scan to connect: <strong>http://{{ ip }}:5000</strong></p>
        </div>

        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <button type="submit">Upload</button>
        </form>

        <h2>File List</h2>
<ul>
    {% for file in files %}
        <li>
            {% if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')) %}
                <img src="{{ url_for('download_file', filename=file) }}" width="100">
                <span>{{ file }}</span>
            {% elif file.lower().endswith(('.mp4', '.webm', '.ogg')) %}
                <video width="200" controls>
                    <source src="{{ url_for('download_file', filename=file) }}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                <span>{{ file }}</span>
            {% elif file.lower().endswith(('.mp3', '.wav', '.ogg')) %}
                <audio controls>
                    <source src="{{ url_for('download_file', filename=file) }}" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>
                <span>{{ file }}</span>
            {% else %}
                <span><a href="{{ url_for('download_file', filename=file) }}">{{ file }}</a></span>
            {% endif %}
        </li>
    {% endfor %}
</ul>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template_string(HTML_TEMPLATE, files=files, ip=LOCAL_IP)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file uploaded", 400
    file = request.files["file"]
    if file.filename == "":
        return "Empty file name", 400
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return index()

@app.route("/uploads/<filename>")
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)