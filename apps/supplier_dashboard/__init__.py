# 📂 apps/supplier_dashboard/__init__.py
# coding: utf-8

"""
هذا الملف يجعل من مجلد 'supplier_dashboard' حزمة بايثون (Package).
يسمح للمصنع الرئيسي (apps/__init__.py) باستيراد المسارات أو دوال التسجيل.
"""

# يمكنك ترك هذا الملف فارغاً، أو استيراد الـ Blueprint لتسهيل الوصول إليها
from apps.supplier_dashboard.routes import supplier_bp

# هذا التأكيد يضمن أن النظام يتعرف على مكونات هذا التطبيق
__all__ = ['supplier_bp']
