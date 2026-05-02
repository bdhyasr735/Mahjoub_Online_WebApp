from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from . import admin_bp
from core.models.user import User

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if user.role == 'admin':
                login_user(user)
                return redirect(url_for('admin.admin_dashboard'))
            flash("صلاحيات غير كافية.")
        else:
            flash("بيانات الدخول غير صحيحة.")
            
    return render_template('login.html')
