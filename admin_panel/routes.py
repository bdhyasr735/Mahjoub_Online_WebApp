import os
import re
import random
import string
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
    def generate_wallet_id(prefix="W-MAH-"):
        random_digits = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}{random_digits}"

from . import admin_bp
from .auth import handle_admin_login

# --- 1. مسار الطوارئ والترميم الذكي (معالجة لغم vendor_uid والأرصدة) ---
@admin_bp.route('/force-repair-now')
def force_repair():
    report = [] # سجل لتوثيق عمليات الترميم لضمان الشفافية السيادية
    try:
        db.session.rollback() 
        
        # أ. ترميم جدول المستخدمين
        db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'admin';"))
        db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active_account BOOLEAN DEFAULT TRUE;"))
        report.append("✅ تم تحديث أدوار المستخدمين وصلاحيات الحسابات.")

        # ب. معالجة مشكلة (vendor_uid) - إضافة العمود وإزالة قيد Not-Null
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS vendor_uid VARCHAR(100);"))
        db.session.execute(text("ALTER TABLE vendors ALTER COLUMN vendor_uid DROP NOT NULL;"))
        report.append("✅ تم تأمين عمود vendor_uid وتحريره من قيود الإدخال الإلزامية.")

        # ج. ترميم الترسانة المالية (الأرصدة الثلاثة لـ سوقك الذكي)
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS balance_yer FLOAT DEFAULT 0.0;"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS balance_sar FLOAT DEFAULT 0.0;"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS balance_usd FLOAT DEFAULT 0.0;"))
        report.append("✅ تم حقن أعمدة الأرصدة السيادية (YER, SAR, USD) في القاعدة.")

        # د. ترميم الهوية والمحفظة والتوثيق الزمني
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS user_id INTEGER;"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS e_wallet VARCHAR(100);"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS owner_name VARCHAR(150);"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS trade_name VARCHAR(150);"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
        report.append("✅ تم اكتمال ربط المحافظ والهوية التجارية.")

        db.session.commit()
        session['repair_done'] = True

        # بناء واجهة التقرير النهائي للمسؤول
        report_items = "".join([f"<li style='margin-bottom:10px;'>{item}</li>" for item in report])
        return f"""
        <div style="max-width:600px; margin:50px auto; padding:30px; border-radius:15px; box-shadow:0 10px 25px rgba(0,0,0,0.1); font-family:sans-serif; direction:rtl; text-align:right; background:white; border-top: 5px solid #632C8F;">
            <h1 style="color: #632C8F; border-bottom:2px solid #f0f0f0; padding-bottom:15px;">✨ تقرير ترميم الترسانة</h1>
            <ul style="list-style:none; padding:20px 0; color:#333;">
                {report_items}
            </ul>
            <div style="margin-top:30px; padding-top:20px; border-top:1px solid #eee;">
                <p style="color:green; font-weight:bold;">✅ اكتملت كافة عمليات الإصلاح بنجاح!</p>
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

# --- 3. حوكمة الموردين (تعميد الموردين الجدد) ---
@admin_bp.route('/add-supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        try:
            db.session.rollback()
            username = request.form.get('username')
            password = request.form.get('password')
            wallet_id = request.form.get('e_wallet')

            if User.query.filter_by(username=username).first():
                return jsonify({"status": "error", "message": f"اسم المستخدم ({username}) مسجل مسبقاً."})
            
            if Vendor.query.filter_by(e_wallet=wallet_id).first():
                return jsonify({"status": "error", "message": f"الرقم السيادي ({wallet_id}) مستخدم بالفعل."})

            # 1. إنشاء حساب المستخدم
            new_user = User(username=username, role='vendor')
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.flush() 

            # 2. إنشاء بيانات المورد (مع تصفير الأرصدة لضمان التوافق مع الترسانة)
            new_vendor = Vendor(
                user_id=new_user.id,
                owner_name=request.form.get('owner_name'),
                trade_name=request.form.get('trade_name'),
                phone=request.form.get('phone'),
                e_wallet=wallet_id,
                balance_yer=0.0,
                balance_sar=0.0,
                balance_usd=0.0,
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
        return render_template('manage_suppliers.html', suppliers=[])

# --- 4. الهندسة المالية وإدارة المحافظ ---
@admin_bp.route('/withdraw-requests')
@login_required
def withdraw_requests():
    try:
        db.session.rollback()
        requests_list = WithdrawRequest.query.order_by(WithdrawRequest.id.desc()).all() if WithdrawRequest else []
        return render_template('withdraw_requests.html', requests=requests_list)
    except:
        return render_template('withdraw_requests.html', requests=[])

@admin_bp.route('/wallets')
@login_required
def manage_wallets():
    try:
        db.session.rollback()
        vendors_list = Vendor.query.all() if Vendor else []
        return render_template('wallets.html', vendors=vendors_list)
    except Exception as e:
        flash(f"خطأ في الوصول للمحافظ: {str(e)}", "danger")
        return redirect(url_for('admin.admin_dashboard'))

# --- 5. إدارة الجلسات السيادية ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if getattr(current_user, 'role', 'admin') == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
    return handle_admin_login()

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('تم إغلاق الجلسة الآمنة بنجاح.', 'info')
    return redirect(url_for('admin.login'))
