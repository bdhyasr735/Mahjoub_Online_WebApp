# coding: utf-8
import os
import hashlib
from apps.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# تهيئة مشفر البيانات السيادي
encryption_key = os.getenv('ENCRYPTION_KEY')
if not encryption_key:
    print("⚠️ تحذير أمني سيادي: ENCRYPTION_KEY غير موجود! تم تشغيل المفتاح المؤقت للمشرفين.")
    encryption_key = '00000000000000000000000000000000'

cipher = AESCipher(encryption_key)

class AdminUser(db.Model, UserMixin):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # حقول التخزين المشفرة في قاعدة البيانات (Ciphertext)
    full_name_enc = db.Column('full_name', db.String(255), nullable=False)
    email_enc = db.Column('email', db.String(255), nullable=False) # تم إزالة UNIQUE من النص المشفر
    
    # ⚡ الـ Blind Index: هاش برمجى فريد ومفهرس للتحقق من عدم تكرار البريد الإلكتروني والبحث السريع عنه دون فك تشفيره
    email_hash = db.Column('email_hash', db.String(64), unique=True, nullable=False, index=True)
    
    # الحقول الإدارية وحسابات الدخول
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='admin', nullable=False)
    
    # الاعتماد على وقت الخادم السحابي للتسجيل الدقيق لعمليات الدخول
    last_login = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # --- بوابات التشفير التلقائي (Properties) ---

    @property
    def full_name(self):
        try: return cipher.decrypt(self.full_name_enc)
        except Exception: return ""
    @full_name.setter
    def full_name(self, value): 
        self.full_name_enc = cipher.encrypt(str(value))

    @property
    def email(self):
        try: return cipher.decrypt(self.email_enc)
        except Exception: return ""
    @email.setter
    def email(self, value):
        clean_email = str(value).strip().lower()
        self.email_enc = cipher.encrypt(clean_email)
        # توليد الـ Blind Index تلقائياً لفراده البريد في قاعدة البيانات
        self.email_hash = hashlib.sha256(clean_email.encode('utf-8')).hexdigest()

    # --- إدارة حماية وهاش كلمات المرور (Password Security) ---

    @property
    def password(self):
        raise AttributeError('❌ كلمة المرور ليست حرقاً قابلاً للقراءة الخارجي!')

    @password.setter
    def password(self, password):
        """توليد هاش معقد ومحمي لكلمة المرور عند تعيينها"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """التحقق الآمن من مطابقة كلمة المرور أثناء تسجيل الدخول"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<AdminUser {self.username} - Role: {self.role}>'
