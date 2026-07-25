from apps.services import services

# استدعاء الخدمات مباشرة وب بكل سهولة:
all_products = services.products.get_all()
all_collections = services.collections.get_all()
