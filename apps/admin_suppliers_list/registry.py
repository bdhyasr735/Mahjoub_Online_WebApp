# coding: utf-8
# 📂 apps/admin_suppliers_list/registry.py

from apps.admin_suppliers_list.routes import suppliers_list_bp

def register_module(app):
    """تسجيل موديول 'سجل الشركاء' مع نافذة التفاصيل الخاصة."""
    
    # تسجيل الـ Blueprint الخاص بالموردين
    app.register_blueprint(suppliers_list_bp, url_prefix='/admin/suppliers')
    
    # ملاحظة: إذا كنت ستعتمد مساراً خاصاً للنافذة المنبثقة (مثلاً للـ AJAX)، 
    # فالمسارات المحددة في routes.py تحت هذا الـ prefix ستغطي ذلك.
    
    print("✅ [Registry]: تم تسجيل موديول 'admin_suppliers_list' وتفعيل نوافذ التفاصيل بنجاح.")
