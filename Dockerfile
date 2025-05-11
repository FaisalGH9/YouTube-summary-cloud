# استخدم صورة رسمية تحتوي Python
FROM python:3.10-slim

# إعداد متغير البيئة لتفادي التحذيرات
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# إنشاء مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ ملفات المشروع
COPY . .

# تثبيت ffmpeg إذا كنت تستخدمه
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean

# تثبيت المتطلبات
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# فتح المنفذ المستخدم بواسطة Streamlit
EXPOSE 8501

# أمر التشغيل
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
