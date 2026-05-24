# coding: utf-8
from flask import Blueprint

wallet_blueprint = Blueprint(
    'wallet', 
    __name__, 
    template_folder='templates'  # يخبر Flask بالبحث داخل مجلد templates الملازم للملف
)
