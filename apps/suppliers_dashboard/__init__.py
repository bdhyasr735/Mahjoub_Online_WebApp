# coding: utf-8
# 📂 apps/suppliers_dashboard/__init__.py

"""
حزمة لوحة تحكم الموردين (Suppliers Dashboard)
هذا الملف يضمن التعامل مع المجلد كحزمة بايثون، 
ويسمح بالاستيراد السلس داخل الموديول.
"""

# يمكننا استيراد البلوبرينت هنا إذا أردت تسهيل الوصول إليها من خارج الموديول
from apps.suppliers_dashboard.routes import dashboard_bp

# لا نحتاج لإضافة الكثير هنا، فقط نضمن أن الموديول متاح
__all__ = ['dashboard_bp']
