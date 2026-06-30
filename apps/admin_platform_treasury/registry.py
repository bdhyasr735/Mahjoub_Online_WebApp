# coding: utf-8
from .routes import treasury_bp

def register_module(app):
    # تسجيل الـ Blueprint مباشرة من خلال النظام التلقائي (Auto-Discovery)
    app.register_blueprint(treasury_bp, url_prefix='/admin/treasury')
    print("✅ [Registry]: تم تسجيل موديول 'الخزينة' بنجاح.")
