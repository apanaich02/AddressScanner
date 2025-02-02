from flask import Flask, request, jsonify
import pytesseract
import os
from PIL import Image
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend access

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_address(image_path):
    """Extract address from an image using OCR"""
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)

    # Address pattern (adjust as needed)
    address_pattern = r"\d+\s[\w\s]+,\s[\w\s]+,\s[A-Z]{2}\s\d{5}"
    addresses = re.findall(address_pattern, text)

    return addresses if addresses else ["No address found"]

@app.route("/upload", methods=["POST"])
def upload():
    """Endpoint to upload an image and extract addresses"""
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    file = request.files["image"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    addresses = extract_address(filepath)
    os.remove(filepath)  # Cleanup

    return jsonify({"addresses": addresses})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
