from flask import Flask, request, send_file
from io import BytesIO
from PIL import Image

app = Flask(__name__)


@app.route('/generate', methods=['POST'])
def generate():
    if 'file' not in request.files:
        return "No file provided", 400

    file = request.files['file']

    try:
        image = Image.open(file)
        img_io = BytesIO()
        image.save(img_io, 'JPEG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpeg')
    except Exception as e:
        return f"Error processing image: {e}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)