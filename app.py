from flask import Flask, request, jsonify
import pytesseract
import os
from PIL import Image
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set Tesseract Path for Render Deployment
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def extract_text(image_path):
    """Extract all text from an image using Tesseract OCR"""
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)  # No filtering, return raw text
    return text.strip()  # Strip leading/trailing whitespace

@app.route("/")
def home():
    return "Address Scanner API is running!"

@app.route("/upload", methods=["POST"])
def upload():
    """Upload an image and return extracted text"""
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    file = request.files["image"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    extracted_text = extract_text(filepath)
    os.remove(filepath)  # Cleanup temporary file

    return jsonify({"text": extracted_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
