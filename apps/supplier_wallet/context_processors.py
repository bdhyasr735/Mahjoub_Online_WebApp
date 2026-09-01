# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/context_processors.py

from flask import current_app

def inject_supplier_modules():
    """حقن الموديولات في القائمة الجانبية"""
    supplier_modules = {}
    
    try:
        if hasattr(current_app, 'supplier_modules'):
            supplier_modules = current_app.supplier_modules.copy()
    except Exception as e:
        print(f"⚠️ [Context Processor Error]: {str(e)}")
    
    return {'supplier_modules': supplier_modules}
