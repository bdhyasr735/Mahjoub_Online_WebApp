from flask import render_template, request, redirect, url_for
from flask_login import login_required
from . import supplier_bp

@supplier_bp.route('/login')
def login():
    # استخدام اسم الملف الذي ذكرته في القائمة
    return render_template('supplier_panel/supplier_login.html')

@supplier_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('supplier_panel/dashboard.html')

@supplier_bp.route('/add-product')
@login_required
def add_product():
    return render_template('supplier_panel/add_product.html')

@supplier_bp.route('/waiting-approval')
def waiting_approval():
    return render_template('supplier_panel/waiting_approval.html')
