import os
from flask import render_template, request, redirect, url_for, flash, session, current_app, jsonify
from flask_login import login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from core import db 

# --- استيراد النماذج (Models) مع معالجة الأخطاء لضمان تشغيل السيرفر ---
try:
    from core.models.vendor import Vendor
    from core.models.user import User  
    from core.models.vendor import WithdrawRequest 
except ImportError:
    Vendor = None
    User = None
    WithdrawRequest = None

# --- استيراد مدير الأرشفة السيادي (GitHub Archive) ---
try:
    from .archive_manager import ArchiveManager
    archiver = ArchiveManager()
except (ImportError, Exception):
    archiver = None

from . import admin_bp
from .auth import handle_admin_login

# --- 1. بوابة الدخول والخروج ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """بوابة الدخول إلى النظام السيادي"""
    return handle_admin_login()

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash("تم تأمين الخروج من النظام السيادي.", "info")
    return redirect(url_for('admin.login'))

# --- 2. لوحة التحكم الرئيسية ---
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    """عرض إحصائيات منصة محجوب أونلاين"""
    suppliers_count = Vendor.query.count() if Vendor else 0
    pending_withdrawals = WithdrawRequest.query.filter_by(status='pending').count() if WithdrawRequest else 0
    return render_template('dashboard.html', 
                           suppliers_count=suppliers_count, 
                           pending_withdrawals=pending_withdrawals)

# --- 3. إدارة الموردين (التعميد والأرشفة) ---
@admin_bp.route('/add-supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():
    """
    إدارة عملية التعميد السيادي الكاملة وتوليد الرقم MAH-9631 وتوابعه
    """
    # أ- توليد المعرف السيادي التالي (تلقائي للعرض في GET)
    next_id = "MAH-9631"
    try:
        if Vendor:
            last_vendor = Vendor.query.order_by(Vendor.id.desc()).first()
            if last_vendor and last_vendor.e_wallet:
                # استخراج الرقم وزيادته (مثلاً من MAH-9631 إلى MAH-9632)
                current_num = int(last_vendor.e_wallet.split('-')[1])
                next_id = f"MAH-{current_num + 1}"
    except Exception:
        next_id = "MAH-9631"

    if request.method == 'POST':
        try:
            # 1. استلام البيانات الأساسية
            username = request.form.get('username')
            password = request.form.get('password', '123')
            e_wallet = request.form.get('e_wallet') # الرقم الذي تم تأكيده في الواجهة
            
            # معالجة نوع النشاط (يدوي أو من القائمة)
            activity = request.form.get('manual_activity') if request.form.get('activity_type') == 'manual' else request.form.get('activity_type')
            
            # 2. الأرشفة السيادية الضوئية (GitHub)
            github_path = "Local_Archive_Only"
            id_file = request.files.get('id_image')
            
            if archiver and id_file and id_file.filename:
                ext = os.path.splitext(id_file.filename)[1]
                file_data = id_file.read()
                
                # رفع الوثيقة للأرشيف العالمي
                github_path = archiver.upload_document(
                    s_id=e_wallet, 
                    u_id=username, 
                    doc_t="Identity_Doc", 
                    file_d=file_data, 
                    ext=ext
                )
                
                # توثيق بيانات المورد في سجل الأرشفة
                archiver.upload_full_package(
                    data={
                        'sovereign_id': e_wallet,
                        'owner_name': request.form.get('owner_name'),
                        'trade_name': request.form.get('trade_name'),
                        'verification_date': os.popen('date').read().strip(),
                        'status': 'Verified_By_Ali_Mahjoub'
                    }
                )

            # 3. إنشاء حساب المستخدم (User)
            new_user = User(
                username=username,
                password=generate_password_hash(password),
                role='vendor'
            )
            db.session.add(new_user)
            db.session.flush() # الحصول على ID المستخدم قبل الحفظ النهائي

            # 4. إنشاء سجل المورد (Vendor) وربطه بالحساب والأرشيف
            new_vendor = Vendor(
                user_id=new_user.id,
                owner_name=request.form.get('owner_name'),
                id_type=request.form.get('id_type'),
                id_card_number=request.form.get('id_card_number'),
                id_image_path=github_path, # مسار الأرشيف في GitHub
                trade_name=request.form.get('trade_name'),
                activity_type=activity,
                province=request.form.get('province'),
                district=request.form.get('district'),
                address_detail=request.form.get('address_detail'),
                phone=request.form.get('phone'),
                e_wallet=e_wallet,
                fin_type=request.form.get('fin_type'),
                bank_name=request.form.get('bank_name'),
                bank_acc=request.form.get('bank_acc'),
                is_verified=True
            )
            
            db.session.add(new_vendor)
            db.session.commit()

            return jsonify({"status": "success", "message": "تم التعميد والأرشفة بنجاح"}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": f"فشل النظام السيادي: {str(e)}"}), 500

    return render_template('add_supplier.html', next_id=next_id)

# --- 4. طلبات السحب والمحافظ ---
@admin_bp.route('/withdraw-requests')
@login_required
def withdraw_requests():
    """مراقبة طلبات سحب الأرباح"""
    requests_list = WithdrawRequest.query.filter_by(status='pending').all() if WithdrawRequest else []
    return render_template('withdraw_requests.html', requests=requests_list)

@admin_bp.route('/wallets')
@login_required
def wallets():
    """كشف المحافظ السيادية للموردين"""
    all_vendors = Vendor.query.all() if Vendor else []
    return render_template('wallets.html', vendors=all_vendors)
