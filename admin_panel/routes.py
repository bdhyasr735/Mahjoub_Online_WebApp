import os
import re
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import text
from core import db 

# --- استيراد النماذج بحذر شديد لضمان استقرار النظام ---
try:
    from core.models.user import User
    from core.models.vendor import Vendor
except ImportError:
    User = None
    Vendor = None

try:
    from core.models.vendor import WithdrawRequest 
except ImportError:
    WithdrawRequest = None

# --- الربط السيادي مع ملف الخدمات (عقل المحفظة) ---
try:
    from services.wallet_service import generate_wallet_id
except ImportError:
    # دالة احتياطية في حال تعثر استيراد الملف المنفصل
    def generate_wallet_id(prefix="W-MAH-"):
        import random
        return f"{prefix}{random.randint(1000, 9999)}"

from . import admin_bp
from .auth import handle_admin_login

# --- 1. مسار الطوارئ السيادي (إصلاح شامل لقاعدة البيانات) ---
@admin_bp.route('/force-repair-now')
def force_repair():
    try:
        db.session.rollback() 
        # تنفيذ أوامر الترميم لضمان وجود كافة الأعمدة التي تسببت في التعثر سابقاً
        db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'admin';"))
        db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active_account BOOLEAN DEFAULT TRUE;"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS user_id INTEGER;"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS e_wallet VARCHAR(100);"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS owner_name VARCHAR(150);"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS trade_name VARCHAR(150);"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
        
        db.session.commit()
        session['repair_done'] = True
        return """
        <div style="text-align:center; margin-top:50px; font-family:sans-serif; direction:rtl;">
            <h1 style="color: #632C8F;">✨ تم اكتمال الترميم الهيكلي بنجاح!</h1>
            <p style="color: #1a0b2e;">تم تحديث الجداول لتتوافق مع معايير محجوب أونلاين.</p>
            <a href="/admin/dashboard" style="padding:12px 25px; background:#632C8F; color:white; text-decoration:none; border-radius:10px;">دخول مركز القيادة (Dashboard)</a>
        </div>
        """
    except Exception as e:
        db.session.rollback()
        return f"<h1 style='color:red; text-align:center;'>❌ فشل الترميم: {str(e)}</h1>"

# --- 2. لوحة التحكم المركزية (الداشبورد) ---
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    try:
        db.session.rollback()
        stats = {'suppliers_count': 0, 'pending_withdrawals': 0, 'orders_count': 0, 'total_balance': "0.00"}
        show_repair = not session.get('repair_done', False)

        if Vendor:
            stats['suppliers_count'] = db.session.query(Vendor).count()
        if WithdrawRequest:
            stats['pending_withdrawals'] = db.session.query(WithdrawRequest).filter_by(status='pending').count()
        
        return render_template('dashboard.html', **stats, show_repair=show_repair)
    except Exception:
        db.session.rollback()
        return render_template('dashboard.html', suppliers_count=0, pending_withdrawals=0, show_repair=True)

# --- 3. حوكمة الموردين وتعيدهم (مع دمج خدمة المحفظة) ---
@admin_bp.route('/add-supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():
    try:
        db.session.rollback()
    except:
        pass
    
    if request.method == 'POST':
        try:
            # استخراج البيانات من نموذج سوقك الذكي
            username = request.form.get('username')
            password = request.form.get('password')
            trade_name = request.form.get('trade_name')
            owner_name = request.form.get('owner_name')
            phone = request.form.get('phone')
            wallet_id = request.form.get('e_wallet') # القيمة القادمة من الواجهة

            if not User or not Vendor:
                return jsonify({"status": "error", "message": "نماذج البيانات غير محملة بشكل صحيح"}), 500

            # فحص التكرار لضمان عدم تعطل الترسانة
            if User.query.filter_by(username=username).first():
                return jsonify({"status": "error", "message": f"اسم المستخدم ({username}) مسجل مسبقاً."})
            
            if Vendor.query.filter_by(e_wallet=wallet_id).first():
                return jsonify({"status": "error", "message": f"الرقم السيادي ({wallet_id}) مستخدم بالفعل."})

            # 1. إنشاء حساب المستخدم
            new_user = User(username=username, role='vendor')
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.flush() 

            # 2. إنشاء بيانات المورد (التعميد الأبدي)
            new_vendor = Vendor(
                user_id=new_user.id,
                owner_name=owner_name,
                trade_name=trade_name,
                phone=phone,
                e_wallet=wallet_id,
                id_type=request.form.get('id_type'),
                id_card_number=request.form.get('id_card_number'),
                activity_type=request.form.get('activity_type'),
                province=request.form.get('province'),
                district=request.form.get('district'),
                address_detail=request.form.get('address_detail'),
                bank_name=request.form.get('bank_name'),
                bank_acc=request.form.get('bank_acc'),
                fin_type=request.form.get('fin_type')
            )
            db.session.add(new_vendor)
            db.session.commit()
            
            return jsonify({"status": "success", "message": "تم الأرشفة والتعميد السيادي بنجاح"})

        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": f"تعثر في الترسانة: {str(e)}"}), 500

    # منطق GET: استدعاء "خدمة المحفظة" لتوليد الرقم الجديد تلقائياً
    next_id = generate_wallet_id() 
    
    return render_template('add_supplier.html', next_id=next_id)

@admin_bp.route('/suppliers')
@login_required
def manage_suppliers():
    try:
        db.session.rollback()
        suppliers_list = Vendor.query.all() if Vendor else []
        return render_template('manage_suppliers.html', suppliers=suppliers_list)
    except:
        db.session.rollback()
        return render_template('manage_suppliers.html', suppliers=[])

# --- 4. الهندسة المالية (طلبات السحب) ---
@admin_bp.route('/withdraw-requests')
@login_required
def withdraw_requests():
    try:
        db.session.rollback()
        requests_list = WithdrawRequest.query.order_by(WithdrawRequest.id.desc()).all() if WithdrawRequest else []
        return render_template('withdraw_requests.html', requests=requests_list)
    except:
        db.session.rollback()
        return render_template('withdraw_requests.html', requests=[])

# --- 5. إدارة الجلسات السيادية ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        db.session.rollback()
        if current_user.is_authenticated:
            user_role = getattr(current_user, 'role', 'admin')
            if user_role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
        return handle_admin_login()
    except:
        return handle_admin_login()

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('تم إغلاق الجلسة الآمنة بنجاح.', 'info')
    return redirect(url_for('admin.login'))
