# coding: utf-8
# 📂 apps/admin_financial_management/routes.py

from flask import Blueprint, render_template
from flask_login import login_required

# تأكد أن هذا الاسم يطابق تماماً ما هو موجود في registry.py
financial_bp = Blueprint(
    'financial_bp', 
    __name__, 
    template_folder='templates'
)

@financial_bp.route('/', methods=['GET'])
@login_required
def index():
    # هنا ستضع الكود الخاص بجلب البيانات (transactions)
    # وتمريرها للقالب admin_financial_management.html
    return render_template('admin_financial_management/admin_financial_management.html')
