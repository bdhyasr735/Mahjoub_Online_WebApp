# coding: utf-8
from flask import Flask, redirect, url_for
import os
from models.admin_db import db, AdminUser

def create_app():
    app = Flask(__name__, template_folder='apps/templates')
    app.secret_key = os.environ.get('SECRET_KEY') or 'MAHJOUB_SECURE_2026'

    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///mahjoub_admin.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from apps.auth_portal.routes import auth_bp
    from apps.admin_dashboard import admin_dashboard  
    from apps.add_supplier.routes import admin_suppliers

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_dashboard, url_prefix='/admin')
    app.register_blueprint(admin_suppliers, url_prefix='/admin/suppliers')

    with app.app_context():
        db.create_all()

    @app.route('/')
    def root():
        return redirect(url_for('auth_portal.login')) 

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
