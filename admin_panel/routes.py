import os
import re
import random
import string
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import text
from core import db 

# --- استيراد النماذج بحذر لضمان استقرار النظام ---
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

# --- الربط السيادي مع ملف الخدمات (عقل المحفظة المحدث) ---
try:
    from services.wallet_service import generate_wallet_id
except ImportError:
    # دالة احتياطية في حال فشل الاستيراد تعتمد الآن على النمط الموحد
    def generate_wallet_id(next_id=None):
        if next_id:
            return f"W-{next_id}"
        return f"W-MAH-{random.randint(9000, 9999)}"

from . import admin_bp
from .auth import handle_admin_login

# دالة مساعدة لحساب المعرف التالي (MAH-XXXX) لضمان دقة الترسانة في العرض
def get_next_sovereign_id():
    try:
        db.session.rollback()
        # نعتمد على عدد الصفوف الحالي + 1 لضمان التسلسل المتطابق مع منطق Core
        count = db.session.query(Vendor).count()
        return f"MAH-963{count + 1}"
    except:
        return f"MAH-963{random.randint(1, 99)}"

# --- 1. مسار الطوارئ والترميم العميق ---
@admin_bp.route('/force-repair-now')
def force_repair():
    report = []
    try:
        db.session.rollback() 
        db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'admin';"))
        db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active_account BOOLEAN DEFAULT TRUE;"))
        report.append("✅ تم تحديث أدوار المستخدمين وصلاحيات الحسابات.")

        legacy_columns = ['vendor_uid', 'username', 'email', 'status']
        for col in legacy_columns:
            db.session.execute(text(f"ALTER TABLE vendors ADD COLUMN IF NOT EXISTS {col} VARCHAR(255);"))
            db.session.execute(text(f"ALTER TABLE vendors ALTER COLUMN {col} DROP NOT NULL;"))
            report.append(f"✅ تم تحرير العمود القديم ({col}) من قيود الإدخال الإلزامية.")

        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS balance_yer FLOAT DEFAULT 0.0;"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS balance_sar FLOAT DEFAULT 0.0;"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS balance_usd FLOAT DEFAULT 0.0;"))
        report.append("✅ تم حقن وتأمين أعمدة الأرصدة السيادية (YER, SAR, USD).")

        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS user_id INTEGER;"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS e_wallet VARCHAR(100);"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
        report.append("✅ تم اكتمال ربط المحافظ والتوثيق الزمني للهوية التجارية.")

        db.session.commit()
        session['repair_done'] = True

        report_items = "".join([f"<li style='margin-bottom:10px;'>{item}</li>" for item in report])
        return f"""
        <div style="max-width:600px; margin:50px auto; padding:30px; border-radius:15px; box-shadow:0 10px 25px rgba(0,0,0,0.1); font-family:sans-serif; direction:rtl; text-align:right; background:white; border-top: 5px solid #632C8F;">
            <h1 style="color: #632C8F; border-bottom:2px solid #f0f0f0; padding-bottom:15px;">✨ تقرير الترميم العميق</h1>
            <ul style="list-style:none; padding:20px 0; color:#333;">{report_items}</ul>
            <div style="margin-top:30px; padding-top:20px; border-top:1px solid #eee;">
                <p style="color:green; font-weight:bold;">✅ تم تنظيف كافة القيود القديمة وتحديث القاعدة بنجاح!</p>
                <a href="/admin/dashboard" style="display:inline-block; margin-top:10px; padding:12px 25px; background:#632C8F; color:white; text-decoration:none; border-radius:8px;">العودة لمركز القيادة</a>
            </div>
        </div>
        """
    except Exception as e:
        db.session.rollback()
        return f"<div style='direction:rtl; text-align:center; padding:50px;'><h1 style='color:red;'>❌ فشل الترميم العميق</h1><code>{str(e)}</code></div>"

# --- 2. لوحة التحكم المركزية ---
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    try:
        db.session.rollback()
        stats = {'suppliers_count': 0, 'pending_withdrawals': 0, 'orders_count': 0}
        show_repair = not session.get('repair_done', False)

        if Vendor:
            stats['suppliers_count'] = db.session.query(Vendor).count()
        if WithdrawRequest:
            stats['pending_withdrawals'] = db.session.query(WithdrawRequest).filter_by(status='pending').count()
        
        return render_template('dashboard.html', **stats, show_repair=show_repair)
    except Exception:
        db.session.rollback()
        return render_template('dashboard.html', suppliers_count=0, pending_withdrawals=0, show_repair=True)

# --- 3. حوكمة الموردين (تعميد الموردين الجدد) ---
@admin_bp.route('/add-supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        try:
            db.session.rollback()
            username = request.form.get('username')
            password = request.form.get('password')
            
            # --- 🛡️ استلام المعرفات السيادية من النموذج لضمان التطابق مع ما رآه المستخدم ---
            # نستخدم الحقول المخفية أو الظاهرة في القالب (next_id و e_wallet)
            received_id = request.form.get('next_id')
            received_wallet = request.form.get('e_wallet')

            if User.query.filter_by(username=username).first():
                return jsonify({"status": "error", "message": f"اسم المستخدم ({username}) مسجل مسبقاً."})

            # 1. إنشاء حساب المستخدم
            new_user = User(username=username, role='vendor')
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.flush() 

            # 2. إنشاء بيانات المورد بالمعرفات السيادية الموحدة
            new_vendor = Vendor(
                user_id=new_user.id,
                vendor_uid=received_id, # MAH-9631
                owner_name=request.form.get('owner_name'),
                trade_name=request.form.get('trade_name'),
                phone=request.form.get('phone'),
                e_wallet=received_wallet, # W-MAH-9631
                balance_yer=0.0, balance_sar=0.0, balance_usd=0.0,
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

    # في حالة GET، القيم يتم توليدها آلياً بواسطة context_processor في core/__init__.py
    return render_template('add_supplier.html')

@admin_bp.route('/suppliers')
@login_required
def manage_suppliers():
    try:
        suppliers_list = Vendor.query.all() if Vendor else []
        return render_template('manage_suppliers.html', suppliers=suppliers_list)
    except:
        return render_template('manage_suppliers.html', suppliers=[])

# --- 4. الهندسة المالية وإدارة المحافظ ---
@admin_bp.route('/withdraw-requests')
@login_required
def withdraw_requests():
    requests_list = WithdrawRequest.query.order_by(WithdrawRequest.id.desc()).all() if WithdrawRequest else []
    return render_template('withdraw_requests.html', requests=requests_list)

@admin_bp.route('/wallets')
@login_required
def manage_wallets():
    vendors_list = Vendor.query.all() if Vendor else []
    return render_template('wallets.html', vendors=vendors_list)

# --- 5. إدارة الجلسات السيادية ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and getattr(current_user, 'role', 'admin') == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    return handle_admin_login()

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('تم إغلاق الجلسة الآمنة بنجاح.', 'info')
    return redirect(url_for('admin.login'))
