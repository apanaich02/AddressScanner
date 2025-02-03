import os
from flask import Flask, request, render_template, jsonify
from PIL import Image
import pytesseract
from pillow_heif import register_heif_opener

# Register HEIC/HEIF support
register_heif_opener()

app = Flask(__name__)

def extract_text(image_path):
    """Extract text from an image using Tesseract OCR with HEIC support."""
    try:
        # Open image
        image = Image.open(image_path)

        # Convert HEIC images to JPG
        if image.format in ["HEIC", "HEIF"]:
            image = image.convert("RGB")  # Convert HEIC to RGB
            image_path = image_path.replace(".heic", ".jpg")
            image.save(image_path, "JPEG")  # Save as JPG

        # Convert to grayscale
        image = image.convert("L")

        # Resize large images to speed up OCR
        max_size = (1000, 1000)
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size)

        # Increase contrast
        image = image.point(lambda x: 0 if x < 160 else 255)

        # Save optimized image temporarily
        temp_path = image_path.replace(".jpg", "_processed.jpg")
        image.save(temp_path)

        # Run OCR with increased timeout
        text = pytesseract.image_to_string(temp_path, timeout=20)  # 20 seconds timeout

        # Cleanup temporary file
        os.remove(temp_path)

        return text.strip()

    except pytesseract.TesseractError:
        return "Error processing image: Tesseract process timeout"

    except Exception as e:
        return f"Error processing image: {str(e)}"


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the image temporarily
    filepath = f"uploads/{image_file.filename}"
    os.makedirs("uploads", exist_ok=True)
    image_file.save(filepath)

    # Extract text
    extracted_text = extract_text(filepath)

    # Delete image after processing
    os.remove(filepath)

    return jsonify({"text": extracted_text})


if __name__ == '__main__':
    app.run(debug=True)
