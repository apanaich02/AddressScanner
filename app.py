from flask import Flask, request, jsonify
import pytesseract
import os
from PIL import Image
import re
from flask_cors import CORS
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)  # Allow frontend access

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🔹 Set the correct path for Tesseract on Render
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def extract_address(image_path):
    """Enhance the image and extract address using OCR"""
    # Load image with OpenCV
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # Convert to grayscale

    # Apply thresholding to remove noise
    image = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Apply dilation and erosion to remove small noise
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.erode(image, kernel, iterations=1)

    # Save preprocessed image temporarily
    temp_path = "processed_image.png"
    cv2.imwrite(temp_path, image)

    # OCR with Tesseract
    text = pytesseract.image_to_string(temp_path)

    # Address extraction using regex (adjust as needed)
    address_pattern = r"\d+\s[\w\s]+,\s[\w\s]+,\s[A-Z]{2}\s\d{3}\s?\d{1}"
    addresses = re.findall(address_pattern, text)

    return addresses if addresses else ["No address found"]

@app.route("/")
def home():
    return "Address Scanner API is running!"

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
