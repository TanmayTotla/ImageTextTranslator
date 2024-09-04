from flask import Flask, render_template, request, send_file,Response
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw, ImageFont
from googletrans import Translator
import io
import os

app = Flask(__name__)

# Initialize the translator
translator = Translator()

# Dictionary to map languages to specific fonts in your fonts folder
font_map = {
    'ar': 'fonts/NotoSansArabic-Regular.ttf',             # Arabic
    'zh-cn': 'fonts/NotoSansCJK-Regular.ttc',             # Chinese Simplified
    'zh-tw': 'fonts/NotoSansCJK-Regular.ttc',             # Chinese Traditional
    'ja': 'fonts/NotoSansCJK-Regular.ttc',                # Japanese
    'ko': 'fonts/NotoSansCJK-Regular.ttc',                # Korean
    'he': 'fonts/NotoSansHebrew-Regular.ttf',             # Hebrew
    'ur': 'fonts/NotoNastaliqUrdu-Regular.ttf',           # Urdu
    'bn': 'fonts/NotoSansBengali-Regular.ttf',            # Bengali
    'th': 'fonts/NotoSansThai-Regular.ttf',               # Thai
    'ta': 'fonts/NotoSansTamil-Regular.ttf',              # Tamil
    'te': 'fonts/NotoSansTelugu-Regular.ttf',             # Telugu
    'ru': 'fonts/NotoSans-Regular.ttf',                   # Russian
    'hi': 'fonts/NotoSansDevanagari-Regular.ttf',         # Hindi
    'pa': 'fonts/NotoSansGurmukhi-Regular.ttf',           # Punjabi (Gurmukhi)
    'gu': 'fonts/NotoSansGujarati-Regular.ttf',           # Gujarati
    'kn': 'fonts/NotoSansKannada-Regular.ttf',            # Kannada
    'ml': 'fonts/NotoSansMalayalam-Regular.ttf',          # Malayalam
    'mr': 'fonts/NotoSansDevanagari-Regular.ttf',         # Marathi
    'or': 'fonts/NotoSansOriya-Regular.ttf',              # Oriya
    'ta': 'fonts/NotoSansTamil-Regular.ttf',              # Tamil
    'si': 'fonts/NotoSansSinhala-Regular.ttf',            # Sinhala
    'my': 'fonts/NotoSansMyanmar-Regular.ttf',            # Burmese
    'lo': 'fonts/NotoSansLao-Regular.ttf',                # Lao
    'km': 'fonts/NotoSansKhmer-Regular.ttf',              # Khmer
    'fa': 'fonts/NotoNaskhArabic-Regular.ttf',            # Persian (Farsi)
    'el': 'fonts/NotoSans-Regular.ttf',                   # Greek (use general Noto Sans)
    'tr': 'fonts/NotoSans-Regular.ttf',                   # Turkish
    'vi': 'fonts/NotoSans-Regular.ttf',                   # Vietnamese
    'de': 'fonts/NotoSans-Regular.ttf',                   # German
    'fr': 'fonts/NotoSans-Regular.ttf',                   # French
    'es': 'fonts/NotoSans-Regular.ttf',                   # Spanish
    'it': 'fonts/NotoSans-Regular.ttf',                   # Italian
    'pt': 'fonts/NotoSans-Regular.ttf',                   # Portuguese
    'en': 'fonts/NotoSans-Regular.ttf',                   # English
    'am': 'fonts/NotoSansEthiopic-Regular.ttf',           # Amharic
    'ti': 'fonts/NotoSansEthiopic-Regular.ttf',           # Tigrinya
    'ti-et': 'fonts/NotoSansEthiopic-Regular.ttf',        # Tigrinya (Ethiopia)
    'ug': 'fonts/NotoSansArabic-Regular.ttf',             # Uyghur
    'yi': 'fonts/NotoSansHebrew-Regular.ttf',             # Yiddish
    'dv': 'fonts/NotoSansThaana-Regular.ttf',             # Dhivehi (Maldivian)
    'ps': 'fonts/NotoSansArabic-Regular.ttf',             # Pashto
    'sd': 'fonts/NotoSansArabic-Regular.ttf',             # Sindhi
    'bo': 'fonts/NotoSerifTibetan-Regular.ttf',           # Tibetan
    'mn': 'fonts/NotoSansMongolian-Regular.ttf',          # Mongolian
    'ka': 'fonts/NotoSansGeorgian-Regular.ttf',           # Georgian
    'si': 'fonts/NotoSansSinhala-Regular.ttf',            # Sinhala
    'hy': 'fonts/NotoSansArmenian-Regular.ttf',           # Armenian
    'ka': 'fonts/NotoSansGeorgian-Regular.ttf',           # Georgian
    'chr': 'fonts/NotoSansCherokee-Regular.ttf',          # Cherokee
    'sa': 'fonts/NotoSansDevanagari-Regular.ttf',         # Sanskrit
    'ckb': 'fonts/NotoSansArabic-Regular.ttf',            # Central Kurdish (Sorani)
    'sdh': 'fonts/NotoSansArabic-Regular.ttf',            # Southern Kurdish
    'ne': 'fonts/NotoSansDevanagari-Regular.ttf',         # Nepali
    'gn': 'fonts/NotoSans-Regular.ttf',                   # Guarani
    'sw': 'fonts/NotoSans-Regular.ttf',                   # Swahili
    'xh': 'fonts/NotoSans-Regular.ttf',                   # Xhosa
    'zu': 'fonts/NotoSans-Regular.ttf',                   # Zulu
    # Add more languages and fonts as needed for other languages present in the list
}


# Default fallback font
default_font = 'fonts/NotoSans-Regular.ttf'  # Use Noto Sans for most languages

# Route to serve the HTML file
@app.route('/')
def index():
    return render_template('index.html')

def expand_bounding_box(x, y, w, h, padding=10):
    """Expand the bounding box by padding."""
    return (x - padding, y - padding, x + w + padding, y + h + padding)

def merge_bounding_boxes(boxes):
    """Merge overlapping or close bounding boxes."""
    if not boxes:
        return []

    # Sort boxes by x-coordinate
    boxes.sort(key=lambda b: b[0])

    merged_boxes = []
    current_box = boxes[0]

    for box in boxes[1:]:
        x1, y1, x2, y2 = current_box
        bx1, by1, bx2, by2 = box

        # Check if the boxes overlap or are close to each other
        if (bx1 <= x2 +100 and bx2 >= x1 - 100 and
            by1 <= y2 +50 and by2 >= y1-50 ):
            # Merge the boxes
            current_box = (min(x1, bx1), min(y1, by1), max(x2, bx2), max(y2, by2))
        else:
            merged_boxes.append(current_box)
            current_box = box

    # Add the last box
    merged_boxes.append(current_box)
    return merged_boxes

# Route to handle image processing
@app.route('/process', methods=['POST'])
def process_image():
    
    # Retrieve the image from the request
    file = request.files['image'].read()
    npimg = np.frombuffer(file, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    # Retrieve the selected language from the form
    selected_language = request.form.get('language')

    # Convert the image to grayscale and use OCR
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    text = ''.join(text)  # Combine individual characters into a single string

    # Get OCR data with bounding boxes
    ocr_data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

    boxes = []
    for i in range(len(ocr_data['text'])):
        if ocr_data['text'][i].strip() != '':
            x, y, w, h = (ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i])
            # Expand bounding box
            x, y, x2, y2 = expand_bounding_box(x, y, w, h)
            boxes.append((x, y, x2, y2))

    # Merge overlapping or close bounding boxes
    merged_boxes = merge_bounding_boxes(boxes)
    
    # Convert image to RGB for color processing
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb_img)
    draw = ImageDraw.Draw(pil_img)

     # Select the appropriate font based on the language
    font_path = font_map.get(selected_language, default_font)
    try:
        font = ImageFont.truetype(font_path, 20)
    except OSError as e:
        print(f"Error loading font: {e}")
        font = ImageFont.load_default()

    def get_average_color(img, x, y, w, h, num_samples=100):
        samples = []
        for _ in range(num_samples):
            px = x + np.random.randint(0, w)
            py = y + np.random.randint(0, h)
            if 0 <= px < img.shape[1] and 0 <= py < img.shape[0]:
                samples.append(img[py, px])
        
        if samples:
            avg_color = np.mean(samples, axis=0)
            avg_color = tuple(map(int, avg_color[::-1]))  # Convert from BGR to RGB
            return avg_color
        return (255, 255, 255)  # Default to white if no color found

    # Function to calculate the average color and invert it
    def get_inverted_color(img, x, y, w, h, num_samples=100):
        samples = []
        for _ in range(num_samples):
            px = x + np.random.randint(0, w)
            py = y + np.random.randint(0, h)
            if 0 <= px < img.shape[1] and 0 <= py < img.shape[0]:
                samples.append(img[py, px])
        
        if samples:
            avg_color = np.mean(samples, axis=0)
            avg_color = tuple(map(int, avg_color[::-1]))  # Convert from BGR to RGB
            # Invert the color
            inverted_color = tuple(255 - c for c in avg_color)
            return inverted_color
        return (255, 255, 255)  # Default to white if no color found

    # Iterate over each merged bounding box
    for i, (x1, y1, x2, y2) in enumerate(merged_boxes):
        # Calculate average color and invert it for text
        avg_color = get_average_color(img, x1, y1, x2 - x1, y2 - y1)        
        # Fill the bounding box with the average color
        draw.rectangle([x1, y1, x2, y2], fill=avg_color)
        

    # Iterate over each detected text and its bounding box
    for i in range(len(ocr_data['text'])):
        if ocr_data['text'][i].strip() != '':
            x, y, w, h = (ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i])
            font_size = (1.1)*h  # Use height of bounding box as font size
            # Ensure font size is reasonable
            font_size = max(10, min(font_size, 50))
             # Load the font with the size corresponding to the bounding box height
            try:
                font = ImageFont.truetype(font_path, font_size)
            except OSError as e:
                print(f"Error loading font: {e}")
                font = ImageFont.load_default()

            color = get_inverted_color(rgb_img, x, y, w, h)
            # Translate the text
            try:
                translated_text = translator.translate(text, dest=selected_language).text
            except ValueError as e:
                print(f"Translation error: {e}")
                translated_text = translator.translate(text, dest=selected_language).text
            # Overlay the translated text back onto the image at the correct position
            draw.text((20, 20), translated_text, fill=color, font=font)
            break

    processed_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    # Save to an in-memory file
    _, buffer = cv2.imencode('.jpg', processed_img)
    return send_file(
        io.BytesIO(buffer),
        mimetype='image/jpeg'
    )

if __name__ == '__main__':
    app.run(debug=True)