import re
from flask import Flask, request, jsonify
import base64
from PIL import Image
import io
import pytesseract

app = Flask(__name__)

@app.route("/ocr", methods=["POST"])
def ocr():
    data = request.json
    image_b64 = data.get("imageBase64")
    if not image_b64:
        return jsonify({"error": "No image provided"}), 400

    # تبدیل Base64 به تصویر
    image_bytes = base64.b64decode(image_b64)
    image = Image.open(io.BytesIO(image_bytes))

    # استخراج متن با Tesseract
    text = pytesseract.image_to_string(image, lang="fas+eng+ara")

    # پاکسازی متن برای خوانایی بهتر
    text = text.replace("\n\n", "\n")  # حذف خطوط خالی اضافی
    text = re.sub(r"\s+\n", "\n", text)  # حذف فضاهای خالی قبل از خطوط
    text = re.sub(r"\n\s+", "\n", text)  # حذف فضاهای خالی بعد از خطوط
    text = text.strip()  # حذف فاصله‌های اول و آخر

    return jsonify({"text": text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
