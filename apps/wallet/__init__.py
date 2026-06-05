# 📂 apps/wallet/__init__.py
from flask import Blueprint

# تعريف الـ Blueprint
wallet_app = Blueprint(
    'wallet_app', 
    __name__, 
    template_folder='templates'
)

# استيراد المسارات (لربطها بالـ Blueprint)
from . import routes
