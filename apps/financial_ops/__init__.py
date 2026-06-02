# 📂 apps/financial_ops/__init__.py

from flask import Blueprint

# تعريف البلوبرينت المالي
financial_bp = Blueprint('financial_ops', __name__, template_folder='templates')

# استيراد المسارات لتفعيلها داخل البلوبرينت
# ملاحظة: يتم الاستيراد هنا لتجنب Circular Imports
from apps.financial_ops import routes

def register_financial_ops(app):
    """تسجيل بلوبرينت العمليات المالية بشكل آمن"""
    try:
        app.register_blueprint(financial_bp, url_prefix='/financial')
        print("✅ تم تسجيل بلوبرينت العمليات المالية (Financial Ops) بنجاح.")
    except Exception as e:
        print(f"❌ فشل تسجيل بلوبرينت العمليات المالية: {e}")
