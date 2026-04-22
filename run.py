from flask import Flask, render_template
from core.models import db
import os

def create_app():
    app = Flask(__name__, 
                template_folder='admin_panel/templates', 
                static_folder='static')
    
    # رابط قاعدة البيانات السحابية (Render)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mahjoub_online_1_db_user:S7dxtVGcKwrsM1QEzGOuPPcRL8dKxgXk@dpg-d79tuthr0fns73epej4g-a/mahjoub_online_1_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'mahjoub_2026_key'

    db.init_app(app)

    @app.route('/')
    def index():
        return render_template('admin/login.html')

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        print("⏳ جاري تنظيف وتجهيز قاعدة بيانات Render...")
        db.drop_all()
        db.create_all()
        print("✅ تم إنشاء الهيكل بنجاح أونلاين!")
    
    app.run(debug=True, port=5000)
