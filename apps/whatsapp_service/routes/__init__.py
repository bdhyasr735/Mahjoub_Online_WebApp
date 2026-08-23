# 📂 apps/whatsapp_service/routes/__init__.py
import os
from flask import Blueprint

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

whatsapp_bp = Blueprint(
    'whatsapp_service',
    __name__,
    template_folder=TEMPLATE_DIR
)

from . import dashboard
