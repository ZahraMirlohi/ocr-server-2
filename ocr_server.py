from flask import Flask, request, jsonify
import base64
import io
import logging
from PIL import Image
import pytesseract
from flask_cors import CORS
import os
import subprocess

app = Flask(__name__)
CORS(app)

# تنظیم خودکار مسیر Tesseract
def setup_tesseract():
    try:
        # بررسی وجود tesseract در مسیرهای مختلف
        possible_paths = [
            '/usr/bin/tesseract',  # لینوکس
            '/usr/local/bin/tesseract',  # لینوکس
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',  # ویندوز
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'  # ویندوز 32-bit
        ]
        
        for path in possible_paths:
            if os.path.isfile(path):
                pytesseract.pytesseract.tesseract_cmd = path
                logger.info(f"Tesseract found at: {path}")
                return True
        
        # اگر پیدا نشد، سعی کنید آن را نصب کنید (برای لینوکس)
        if os.name != 'nt':  # اگر روی لینوکس است
            try:
                subprocess.run(['apt-get', 'update'], check=True)
                subprocess.run(['apt-get', 'install', '-y', 'tesseract-ocr'], check=True)
                pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
                logger.info("Tesseract installed successfully")
                return True
            except Exception as e:
                logger.error(f"Failed to install Tesseract: {str(e)}")
                return False
        else:
            logger.error("Tesseract not found. Please install it manually.")
            return False
            
    except Exception as e:
        logger.error(f"Error setting up Tesseract: {str(e)}")
        return False

# تنظیمات logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# راه اندازی Tesseract هنگام شروع برنامه
if not setup_tesseract():
    logger.warning("Tesseract setup failed. OCR may not work properly.")

# بقیه کد بدون تغییر...
