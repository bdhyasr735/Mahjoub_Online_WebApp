from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user

# تعريف البلوبرينت للموردين
supplier_bp = Blueprint('supplier_panel', __name__, template_folder='templates')

@supplier_bp.route('/login', methods=['GET', 'POST'])
def supplier_login():
    # البحث سيتم داخل supplier_panel/templates/supplier_panel/login.html
    return render_template('supplier_panel/login.html')

@supplier_bp.route('/dashboard')
@login_required
def supplier_dashboard():
    return render_template('supplier_panel/dashboard.html')
