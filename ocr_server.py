from flask import Flask, request, jsonify
import base64
import io
import logging
import os
from PIL import Image
import pytesseract
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# تنظیمات logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تنظیم مسیر Tesseract برای محیط‌های مختلف
try:
    # برای ویندوز
    if os.name == 'nt':
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            logger.info(f"Tesseract path set to: {tesseract_path}")
        else:
            logger.warning("Tesseract not found at default Windows path")
    # برای لینوکس (Railway) - تلاش برای پیدا کردن مسیر
    else:
        # بررسی مسیرهای معمول Tesseract در لینوکس
        possible_paths = [
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract',
            '/app/bin/tesseract'
        ]
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                logger.info(f"Tesseract found at: {path}")
                break
        else:
            logger.warning("Tesseract not found in common Linux paths")
except Exception as e:
    logger.error(f"Error setting Tesseract path: {str(e)}")

@app.route('/ocr-binary', methods=['POST'])
def ocr_binary():
    try:
        logger.info("دریافت درخواست OCR باینری")
        
        # دریافت داده باینری
        image_data = request.get_data()
        
        if not image_data or len(image_data) == 0:
            return jsonify({
                'success': False,
                'error': 'هیچ داده‌ای دریافت نشد'
            }), 400
        
        logger.info(f"اندازه داده دریافتی: {len(image_data)} بایت")
        
        # تبدیل به image object
        try:
            image = Image.open(io.BytesIO(image_data))
            # تبدیل به RGB اگر لازم است
            if image.mode != 'RGB':
                image = image.convert('RGB')
        except Exception as e:
            logger.error(f"خطا در باز کردن تصویر: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'فرمت تصویر نامعتبر است'
            }), 400
        
        # انجام OCR
        try:
            text = pytesseract.image_to_string(image, lang='fas+eng')
            logger.info(f"OCR موفقیت‌آمیز. طول متن: {len(text)} کاراکتر")
            
            return jsonify({
                'success': True,
                'text': text,
                'message': 'OCR successful'
            })
            
        except Exception as e:
            logger.error(f"خطا در پردازش OCR: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'خطا در پردازش OCR: {str(e)}'
            }), 500
        
    except Exception as e:
        logger.error(f"خطای غیرمنتظره: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/ocr', methods=['POST'])
def ocr_base64():
    try:
        data = request.get_json()
        if not data or 'imageBase64' not in data:
            return jsonify({'error': 'لطفاً تصویر را ارسال کنید'}), 400
        
        # استخراج داده base64
        image_base64 = data['imageBase64']
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        
        # decode base64
        try:
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # تبدیل به RGB اگر لازم است
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            text = pytesseract.image_to_string(image, lang='fas+eng')
            
            return jsonify({
                'success': True,
                'text': text,
                'message': 'OCR successful'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'خطا در پردازش تصویر: {str(e)}'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint برای بررسی سلامت سرور"""
    return jsonify({
        'status': 'ok',
        'message': 'سرور در حال اجراست'
    })

@app.route('/', methods=['GET'])
def home():
    """صفحه اصلی"""
    return jsonify({
        'message': 'خوش آمدید به سرور OCR',
        'endpoints': {
            'POST /ocr-binary': 'ارسال تصویر به صورت باینری',
            'POST /ocr': 'ارسال تصویر به صورت base64',
            'GET /health': 'بررسی سلامت سرور'
        }
    })

if __name__ == '__main__':
    # دریافت پورت از متغیر محیطی (برای Railway) یا استفاده از پورت پیش‌فرض
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
