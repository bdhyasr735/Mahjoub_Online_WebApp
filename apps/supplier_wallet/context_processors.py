# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/context_processors.py

from flask import current_app

def inject_supplier_modules():
    """
    حقن الموديولات في القائمة الجانبية
    يستخدم البيانات المسجلة من registry.py
    """
    supplier_modules = {}
    
    # 🔥 استخدام البيانات المسجلة من registry.py
    if hasattr(current_app, 'supplier_modules'):
        supplier_modules = current_app.supplier_modules
        print("🔍 [DEBUG] Context Processor - Using app.supplier_modules")
        print("🔍 [DEBUG] Keys:", list(supplier_modules.keys()))
        
        # التحقق من وجود 'إدارة المالية'
        if 'إدارة المالية' in supplier_modules:
            print("🔍 [DEBUG] 'إدارة المالية' found with links:", 
                  supplier_modules['إدارة المالية'].get('links', {}))
        else:
            print("⚠️ [DEBUG] 'إدارة المالية' NOT found in supplier_modules!")
    else:
        print("⚠️ [DEBUG] app.supplier_modules not found!")
    
    return {
        'supplier_modules': supplier_modules
    }
