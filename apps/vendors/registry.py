# داخل apps/vendors/registry.py
from .routes import vendors_bp # استيراد الـ Blueprint الخاص بك

def register_app(app):
    app.register_blueprint(vendors_bp, url_prefix='/vendors')
