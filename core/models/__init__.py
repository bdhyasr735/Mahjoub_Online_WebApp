from core import db
from core.models.user import User
from core.models.supplier import Supplier
from core.models.product import Product

# تعريف القائمة التي تسمح بالاستيراد النظيف من خارج المجلد
# هذا يمنع تكرار أسطر الاستيراد (Import redundancy) في الـ routes
__all__ = ['User', 'Supplier', 'Product']
