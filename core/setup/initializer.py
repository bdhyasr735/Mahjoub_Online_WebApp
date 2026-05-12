import os
from core.extensions import db

def initialize_sovereign_system(app):
    dirs = [
        'core/models', 'apps/supplier_app/templates', 
        'apps/finance_app/templates', 'static/css', 'static/js'
    ]
    
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
            # إنشاء ملف __init__.py لجعلها حزم
            with open(os.path.join(d, '__init__.py'), 'w') as f: pass
    
    print("✅ تم بناء الهيكل المجلدي.")
    
    # بناء الجداول فقط إذا وجد ملف الموديل
    if os.path.exists('core/models/supplier_db.py'):
        try:
            from core.models.supplier_db import Supplier
            db.create_all()
            print("💎 تم بناء الجداول السيادية.")
        except Exception as e:
            print(f"⚠️ خطأ في بناء الجداول: {e}")
