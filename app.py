from flask import Flask, request, render_template
import os
from PIL import Image
import pytesseract
from pillow_heif import register_heif_opener

# Register HEIC/HEIF support
register_heif_opener()

# Initialize Flask app
app = Flask(__name__, template_folder="templates")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return render_template('index.html', text="Error: No image provided.")

    image_file = request.files['image']
    if image_file.filename == '':
        return render_template('index.html', text="Error: No selected file.")

    # Create upload directory if not exists
    upload_folder = "uploads"
    os.makedirs(upload_folder, exist_ok=True)

    # Save image temporarily
    filepath = os.path.join(upload_folder, image_file.filename)
    image_file.save(filepath)

    try:
        # Open image and convert to RGB (fix HEIC/CMYK issues)
        with Image.open(filepath) as image:
            image = image.convert("RGB")

            # Resize image to 50% of original dimensions
            width, height = image.size
            new_size = (width // 2, height // 2)
            image = image.resize(new_size)

            # Run OCR
            extracted_text = pytesseract.image_to_string(image)

    except Exception as e:
        extracted_text = f"Error processing image: {str(e)}"

    # Delete the image after processing
    os.remove(filepath)

    return render_template('index.html', text=extracted_text)


if __name__ == '__main__':
    app.run(debug=True)
