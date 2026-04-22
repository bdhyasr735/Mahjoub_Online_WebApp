from flask import Flask
from admin_panel.models import db, User  # استيراد القاعدة والموديل
from admin_panel.admin_routes import admin_bp
from flask_login import LoginManager

app = Flask(__name__)

# 1. إعدادات المفتاح السري وقاعدة البيانات
app.config['SECRET_KEY'] = 'mahjoub_secret_key_2026' # مفتاح تشفير الجلسات
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mahjoub_online.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 2. ربط قاعدة البيانات بالتطبيق
db.init_app(app)

# 3. إعداد نظام إدارة الدخول (Login Manager)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin.login' # توجيه المستخدم لهنا إذا حاول الدخول دون إذن

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 4. تسجيل الـ Blueprint الخاص بالإدارة
app.register_blueprint(admin_bp, url_prefix='/admin')

# 5. إنشاء قاعدة البيانات وإضافة "علي محجوب" إذا لم يكن موجوداً
with app.app_context():
    db.create_all()  # إنشاء الملف والجداول
    
    # كود التحقق من وجود القائد
    admin_user = User.query.filter_by(username='علي محجوب').first()
    if not admin_user:
        new_admin = User(username='علي محجوب', role='SuperAdmin')
        new_admin.set_password('123456') # غيرها لاحقاً
        db.session.add(new_admin)
        db.session.commit()
        print("✅ تم إنشاء حساب القائد: علي محجوب")

if __name__ == '__main__':
    app.run(debug=True)
