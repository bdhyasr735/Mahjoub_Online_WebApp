# 1. استخدام نسخة خفيفة من بايثون
FROM python:3.10-slim

# 2. تحديد مجلد العمل داخل السيرفر
WORKDIR /app

# 3. نسخ ملف المتطلبات أولاً لتسريع البناء
COPY requirements.txt .

# 4. تثبيت المكتبات اللازمة
RUN pip install --no-cache-dir -r requirements.txt

# 5. نسخ بقية ملفات المشروع
COPY . .

# 6. تشغيل التطبيق باستخدام Gunicorn على المنفذ 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "run:app"]
