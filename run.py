from flask import Flask, redirect, url_for
from apps.admin_dashboard.routes import admin_bp
# سنضيف تطبيقات الموردين والمالية لاحقاً هنا

app = Flask(__name__)
app.secret_key = 'MAHJOUB_SOVEREIGN_KEY_2026' # مفتاح الأمان للمؤسس

# تسجيل النوافذ (Blueprints) مع تحديد مساراتها
app.register_blueprint(admin_bp, url_prefix='/admin')

@app.route('/')
def root():
    # توجيه تلقائي لمنصة الإدارة
    return redirect(url_for('admin.dashboard'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
