import os
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import logout_user, login_required, current_user
from sqlalchemy import or_
from datetime import datetime

# الاستيراد من الهيكلية المعتمدة لترسانة محجوب أونلاين
from core.extensions import db 
from core.models.supplier import Supplier
from core.models.user import User

from . import admin_bp
from .auth import handle_admin_login

# --- 1. بروتوكول التحقق السيادي (حماية مركز القيادة) ---
def is_admin_sovereign():
    """ يضمن أن المؤسس علي محجوب فقط يمكنه الوصول. """
    return current_user.is_authenticated and getattr(current_user, 'role', '').lower() == 'admin'

# --- 2. بوابة الدخول (The Gateway) ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if is_admin_sovereign(): 
        return redirect(url_for('admin.admin_dashboard'))
    return handle_admin_login()

# --- 3. مركز القيادة (Dashboard) ---
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if not is_admin_sovereign():
        return redirect(url_for('admin.login'))
    
    try:
        suppliers_count = Supplier.query.count()
        users_count = User.query.count()
        
        try:
            from core.models.business import Order
            orders_count = Order.query.count()
        except Exception:
            orders_count = 0

        stats = {
            'suppliers_count': suppliers_count,
            'orders_count': orders_count,
            'users_count': users_count,
            'now': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return render_template('dashboard.html', **stats)
        
    except Exception as e:
        return render_template('dashboard.html', suppliers_count=0, orders_count=0, users_count=0, now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# --- 4. إدارة الموردين (عرض الصفحة) ---
@admin_bp.route('/manage-suppliers')
@login_required
def manage_suppliers():
    if not is_admin_sovereign(): 
        return redirect(url_for('admin.login'))
    return render_template('manage_suppliers.html')

# --- 5. بروتوكول البحث الميداني (API لاستدعاء الموردين) ---
@admin_bp.route('/api/search-supplier', methods=['GET'])
@login_required
def api_search_supplier():
    if not is_admin_sovereign():
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    query = request.args.get('q', '').strip()
    province = request.args.get('province', '').strip()
    district = request.args.get('district', '').strip()

    # القاعدة الأساسية: إذا كان الاستعلام نجمة (*)، نجلب الكل
    if query == '*':
        suppliers_query = Supplier.query
    else:
        # البحث بالاسم التجاري، الهاتف، أو المعرف (بإزالة 963 للبحث في الـ ID الأصلي)
        clean_query = query.replace('963', '').replace('SUP-MAH-', '')
        suppliers_query = Supplier.query.filter(
            or_(
                Supplier.trade_name.contains(query),
                Supplier.phone.contains(query),
                Supplier.id.like(f"%{clean_query}%")
            )
        )

    # تطبيق فلاتر الموقع الجغرافي (نطاق العمليات)
    if province:
        suppliers_query = suppliers_query.filter(Supplier.province == province)
    if district:
        suppliers_query = suppliers_query.filter(Supplier.district == district)

    suppliers = suppliers_query.all()

    if suppliers:
        results = []
        for s in suppliers:
            results.append({
                "id": s.id,
                "trade_name": s.trade_name,
                "phone": s.phone,
                "province": s.province,
                "district": s.district,
                "activity_type": s.activity_type,
                "tier": getattr(s, 'tier', 'مبتدئ'),
                "status": getattr(s, 'status', 'active')
            })
        return jsonify({"status": "success", "suppliers": results})
    
    return jsonify({"status": "error", "message": "No results found"}), 404

# --- 6. بروتوكول تحديث بيانات المورد (Update API) ---
@admin_bp.route('/api/update-supplier/<int:sup_id>', methods=['POST'])
@login_required
def api_update_supplier(sup_id):
    if not is_admin_sovereign():
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    supplier = Supplier.query.get_or_404(sup_id)
    data = request.get_json()

    try:
        supplier.phone = data.get('phone', supplier.phone)
        supplier.activity_type = data.get('activity_type', supplier.activity_type)
        supplier.province = data.get('province', supplier.province)
        supplier.district = data.get('district', supplier.district)
        supplier.tier = data.get('tier', supplier.tier)
        supplier.status = data.get('status', supplier.status)

        db.session.commit()
        return jsonify({"status": "success", "message": "تم التحديث بنجاح"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 400

# --- 7. بروتوكول تعميد مورد جديد ---
@admin_bp.route('/add-supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if not is_admin_sovereign(): 
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        try:
            # (نفس منطق الإضافة السابق الخاص بك)
            new_supplier = Supplier(
                username=request.form.get('username'),
                password=request.form.get('password'),
                owner_name=request.form.get('owner_name'),
                trade_name=request.form.get('trade_name'),
                phone=request.form.get('phone'),
                province=request.form.get('province'),
                district=request.form.get('district'),
                status='active',
                tier='مبتدئ'
            )
            db.session.add(new_supplier)
            db.session.commit()
            if is_ajax: return jsonify({'status': 'success', 'message': 'تم التعميد'})
            return redirect(url_for('admin.manage_suppliers'))
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 400

    last_s = Supplier.query.order_by(Supplier.id.desc()).first()
    current_num = f"963{(last_s.id + 1) if last_s else 1}"
    return render_template('add_supplier.html', next_id=f"SUP-MAH-{current_num}")

# --- 8. تسجيل الخروج ---
@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("تم الخروج الآمن من نظام الإدارة", "info")
    return redirect(url_for('admin.login'))
