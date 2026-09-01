# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/context_processors.py

from flask import current_app

def inject_supplier_modules():
    """
    حقن الموديولات في القائمة الجانبية
    تستخدم البيانات المسجلة من registry.py في app.supplier_modules
    """
    supplier_modules = {}
    
    try:
        # 🔥 جلب الموديولات المسجلة من التطبيق
        if hasattr(current_app, 'supplier_modules'):
            supplier_modules = current_app.supplier_modules.copy()
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
            
    except Exception as e:
        print(f"⚠️ [Context Processor Error]: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return {
        'supplier_modules': supplier_modules
    }
