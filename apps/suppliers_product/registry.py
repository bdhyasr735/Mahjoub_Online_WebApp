# apps/__init__.py (التلقائي)
for item in os.listdir(apps_dir):
    registry_file = os.path.join(item_path, 'registry.py')
    if os.path.exists(registry_file):
        module = importlib.import_module(f"apps.{item}.registry")
        
        # ✅ سيقرأ هذه المتغيرات تلقائياً
        MODULE_NAME = module.MODULE_NAME          # "منتجاتي"
        MODULE_ICON = module.MODULE_ICON          # "fas fa-boxes"
        SHOW_IN_SUPPLIER = module.SHOW_IN_SUPPLIER # True
        LINKS = module.LINKS                      # الروابط
        
        # ✅ سيسجل الموديول
        module.register_module(app)
