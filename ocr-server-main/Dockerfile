FROM python:3.10-slim

# نصب Tesseract و زبان فارسی
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-fas \
    tesseract-ocr-eng \
    tesseract-ocr-ara \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# نصب pip آخرین نسخه
RUN pip install --upgrade pip

# کپی پروژه
WORKDIR /app
COPY . /app

# نصب پکیج‌ها
RUN pip install --no-cache-dir -r requirements.txt

# اجرای سرور
CMD ["gunicorn", "-b", "0.0.0.0:5000", "ocr_server:app"]
