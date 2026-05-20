# coding: utf-8
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
# تأكد من استيراد كائناتك الأساسية من ملف __init__.py الرئيسي
from apps import db 

# هذا هو الاسم الذي يبحث عنه ملف __init__.py
admin_wallet = Blueprint('admin_wallet', __name__)

# أمثلة للمسارات (Routes) داخل هذا البلوبرينت
@admin_wallet.route('/wallet', methods=['GET'])
@login_required
def wallet_page():
    # هنا تضع منطق المحفظة الخاص بك
    return render_template('admin/wallet.html')

# أضف بقية المسارات الخاصة بك هنا تحت نفس الـ Blueprint
