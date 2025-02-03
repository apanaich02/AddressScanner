from flask import Flask, request, jsonify, send_file
import pytesseract
import os
from PIL import Image
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
STATIC_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set Tesseract Path for Render Deployment
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def extract_text(image_path):
    """Extract all text from an image using Tesseract OCR"""
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        return f"Error processing image: {str(e)}"

@app.route("/")
def home():
    return "Address Scanner API is running!"

@app.route("/web")
def web():
    """Serve the HTML page for uploading images"""
    return send_file("static/index.html")

@app.route("/upload", methods=["POST"])
def upload():
    """Upload an image and return extracted text"""
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image provided"}), 400
        
        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        extracted_text = extract_text(filepath)
        os.remove(filepath)  # Cleanup temporary file

        return jsonify({"text": extracted_text})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
