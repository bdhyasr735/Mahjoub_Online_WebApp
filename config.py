import os

class Config:
    # --- إعدادات قاعدة البيانات ---
    # يفضل استخدام DATABASE_URL من متغيرات البيئة في Railway
    uri = os.environ.get('DATABASE_URL') or 'postgresql://mahjoub_online_1_db_user:S7dxtVGcKwrsM1QEzGOuPPcRL8dKxgXk@dpg-d79tuthr0fns73epej4g-a.oregon-postgres.render.com/mahjoub_online_1_db'
    
    # معالجة اختلاف تسمية البروتوكول (ضروري جداً لـ SQLAlchemy)
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # --- إعدادات الأمان والجلسات ---
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Ali_Mahjoub_High_Energy_2026'

    # --- إعدادات الأرشفة السيادية (GitHub Sovereign Assets) ---
    # هنا التعديل الجذري: جلب القيم من Railway Variables التي أضفتها أنت
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN') 
    GITHUB_REPO = os.environ.get('GITHUB_REPO')
    
    # في حال لم تكن المتغيرات موجودة في Railway (للاحتياط فقط)
    if not GITHUB_TOKEN:
        GITHUB_TOKEN = "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"
    if not GITHUB_REPO:
        GITHUB_REPO = "alimohm/Mahjoub-Sovereign-Assets"
    
    # مسار المجلد الرئيسي للأرشفة
    GITHUB_MAIN_PATH = "Main_Archive"
