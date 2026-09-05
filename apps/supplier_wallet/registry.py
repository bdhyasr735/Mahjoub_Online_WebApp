from flask import Blueprint

# تعريف البلوبرنت الخاص بمحفظة الموردين مع تحديد مسار القوالب ومجلدات الـ static إن وجدت
supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/supplier/wallet'
)

def register_supplier_wallet_app(app):
    """
    دالة لتسجيل تطبيق محفظة الموردين وتوابعه في التطبيق الرئيسي Flask
    """
    # استيراد المسارات هنا لتجنب المشاكل الدائرية (Circular Imports)
    from . import routes
    
    # تسجيل الـ Blueprint في التطبيق الرئيسي
    app.register_blueprint(supplier_wallet_bp)
    
    # يمكنك إضافة أي تهيئة إضافية هنا (مثل تسجيل خدمات أو أدوات مساعدة عامة)
    print("Supplier Wallet App registered successfully.")
