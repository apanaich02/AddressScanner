from flask import Flask, request, jsonify, send_file
import pytesseract
import os
from PIL import Image
from flask_cors import CORS
from pillow_heif import register_heif_opener

# Register HEIC format with PIL
register_heif_opener()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
STATIC_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set Tesseract Path for Render Deployment
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def extract_text(image_path):
    """Extract text from an image using Tesseract OCR with preprocessing."""
    try:
        # Open image and convert to grayscale
        image = Image.open(image_path).convert("L")  

        # Reduce image size to speed up OCR (if larger than 1000x1000)
        max_size = (1000, 1000)
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size)

        # Increase contrast for better OCR accuracy
        image = image.point(lambda x: 0 if x < 160 else 255)

        # Save optimized image temporarily
        temp_path = image_path.replace(".jpg", "_processed.jpg")
        image.save(temp_path)

        # Run OCR with increased timeout
        text = pytesseract.image_to_string(temp_path, timeout=20)  # 20-second timeout
        
        # Cleanup temporary file
        os.remove(temp_path)

        return text.strip()
    
    except pytesseract.TesseractError:
        return "Error processing image: Tesseract process timeout"
    
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
    """Upload an image and return extracted text."""
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image provided"}), 400

        file = request.files["image"]

        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        # Convert HEIC to JPG if needed
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        if filename.lower().endswith(".heic"):
            heic_image = Image.open(file)
            filename = filename.replace(".heic", ".jpg")
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            heic_image.save(filepath, format="JPEG")
        else:
            file.save(filepath)

        extracted_text = extract_text(filepath)
        os.remove(filepath)  # Cleanup temporary file

        return jsonify({"text": extracted_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
