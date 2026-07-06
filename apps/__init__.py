# 📂 apps/__init__.py

# ... (نفس الاستيرادات السابقة) ...

# 1. فصل القوائم تماماً (عزل تقني)
ADMIN_MODULES = {}
SUPPLIER_MODULES = {}

# ... (دالة load_user كما هي) ...

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # ... (تهيئة الإضافات الأساسية) ...
    
    # 2. الاكتشاف الذكي مع العزل
    apps_dir = app.root_path 
    ignored_dirs = ['__pycache__', 'models', 'extensions', 'static', 'templates', 'migrations', 'utils', 'api', 'suppliers_auth_portal']
    
    if os.path.exists(apps_dir):
        for item in os.listdir(apps_dir):
            item_path = os.path.join(apps_dir, item)
            
            if os.path.isdir(item_path) and item not in ignored_dirs:
                registry_file = os.path.join(item_path, 'registry.py')
                if os.path.exists(registry_file):
                    try:
                        module = importlib.import_module(f"apps.{item}.registry")
                        if hasattr(module, 'register_module'):
                            module.register_module(app)
                            
                            mod_data = {
                                "display_name": getattr(module, 'MODULE_NAME', item.capitalize()),
                                "icon": getattr(module, 'MODULE_ICON', 'fa-folder'),
                                "links": getattr(module, 'LINKS', {}),
                            }
                            
                            # العزل: إذا كانت الخاصية True نضعها في قائمة المورد، وإلا في الإدارة
                            if getattr(module, 'SHOW_IN_SUPPLIER', False):
                                SUPPLIER_MODULES[item] = mod_data
                            else:
                                ADMIN_MODULES[item] = mod_data
                                
                            print(f"✅ تم تسجيل الموديول: {item} في {'بوابة المورد' if getattr(module, 'SHOW_IN_SUPPLIER', False) else 'بوابة الإدارة'}")
                    except Exception as e:
                        print(f"❌ فشل تسجيل {item}: {e}")

    # 3. حقن المتغيرات (عزل السياق)
    @app.context_processor
    def inject_vars():
        return dict(
            csrf_token=generate_csrf,
            # كل جهة ترى قائمتها فقط
            registered_modules=ADMIN_MODULES, 
            supplier_modules=SUPPLIER_MODULES 
        )

    # ... (باقي الكود كما هو) ...
    return app
