from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from core.models.user import User 
from core import db
from . import admin_bp

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('تم الدخول بنجاح يا قائد.', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('⚠️ بيانات الدخول غير صحيحة.', 'danger')
            
    return render_template('login.html')

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    return render_template('dashboard.html')
