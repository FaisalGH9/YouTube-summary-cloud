# استخدم صورة Python رسمية خفيفة
FROM python:3.10-slim

# إعدادات بيئة تشغيل بايثون
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# إنشاء مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ ملفات المشروع إلى داخل الحاوية
COPY . .

# تثبيت ffmpeg إذا كنت تستخدمه للتعامل مع الصوتيات
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean

# تثبيت المتطلبات
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# فتح المنفذ 8080 (المستخدم في Cloud Run)
EXPOSE 8080

# أمر التشغيل: استخدم المتغير PORT الذي توفره Google Cloud Run تلقائياً
CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
