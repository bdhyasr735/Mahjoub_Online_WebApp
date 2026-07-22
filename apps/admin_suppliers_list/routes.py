# coding: utf-8
# 📂 apps/admin_suppliers_list/routes.py

import json
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet
from apps.models.product_supplier_map import ProductSupplierMapping

# 1. إنشاء الـ Blueprint
suppliers_bp = Blueprint(
    'suppliers_bp', 
    __name__, 
    template_folder='templates'
)


# ============================================================
# 🟣 مسار قائمة الموردين
# ============================================================
@suppliers_bp.route('/list', methods=['GET'])
@login_required
def list_suppliers():
    """عرض قائمة الشركاء المعتمدين."""
    try:
        suppliers = Supplier.query.order_by(Supplier.id.desc()).all()
        
        # ✅ إضافة بيانات المحفظة لكل مورد
        for supplier in suppliers:
            wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
            supplier.wallet_code = wallet.wallet_code if wallet else '---'
            supplier.balance_sar = wallet.balance_sar if wallet else 0
        
        return render_template(
            'admin_suppliers_list/admin_suppliers_list.html', 
            suppliers=suppliers
        )
    except Exception as e:
        flash(f"خطأ في تحميل البيانات: {str(e)}", "danger")
        return redirect(url_for('admin_dashboard_bp.dashboard'))


# ============================================================
# 🟣 مسار تفاصيل الشريك (JSON)
# ============================================================
@suppliers_bp.route('/<int:supplier_id>/details', methods=['GET'])
@login_required
def supplier_details_json(supplier_id):
    """إرجاع تفاصيل الشريك بصيغة JSON."""
    supplier = Supplier.query.get_or_404(supplier_id)
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    
    return jsonify({
        "success": True,
        "supplier": {
            "id": supplier.id,
            "username": supplier.username,
            "supplier_code": supplier.supplier_code,
            "owner_name": supplier.owner_name,
            "trade_name": supplier.trade_name,
            "phone": supplier.phone,
            "status": supplier.status,
            "rank": supplier.rank,
            "created_at": supplier.created_at.strftime('%Y-%m-%d %H:%M') if supplier.created_at else None,
            "wallet_code": wallet.wallet_code if wallet else '---',
            "balance_sar": float(wallet.balance_sar) if wallet and wallet.balance_sar else 0
        }
    })


# ============================================================
# 🟣 مسار عرض تفاصيل الشريك (صفحة)
# ============================================================
@suppliers_bp.route('/details/<int:supplier_id>', methods=['GET'])
@login_required
def supplier_details(supplier_id):
    """عرض صفحة تفاصيل الشريك."""
    supplier = Supplier.query.get_or_404(supplier_id)
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    
    # ✅ جلب عدد المنتجات المرتبطة بالمورد
    products_count = ProductSupplierMapping.query.filter_by(
        supplier_id=supplier_id,
        status='active'
    ).count()
    
    return render_template(
        'admin_suppliers_list/supplier_details.html',
        supplier=supplier,
        wallet=wallet,
        products_count=products_count
    )


# ============================================================
# 🟣 مسار تعديل الشريك
# ============================================================
@suppliers_bp.route('/<int:supplier_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_supplier(supplier_id):
    """تعديل بيانات الشريك."""
    supplier = Supplier.query.get_or_404(supplier_id)
    
    if request.method == 'POST':
        try:
            supplier.trade_name = request.form.get('trade_name', supplier.trade_name)
            supplier.owner_name = request.form.get('owner_name', supplier.owner_name)
            supplier.status = request.form.get('status', supplier.status)
            supplier.rank = request.form.get('rank', supplier.rank)
            
            # ✅ تحديث رقم الهاتف إذا تم تغييره
            new_phone = request.form.get('phone', '')
            if new_phone and new_phone != supplier.phone:
                supplier.phone = new_phone
            
            db.session.commit()
            flash("✅ تم تحديث بيانات الشريك بنجاح.", "success")
            return redirect(url_for('suppliers_bp.list_suppliers'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"❌ حدث خطأ: {str(e)}", "danger")
    
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    
    return render_template(
        'admin_suppliers_list/supplier_edit.html',
        supplier=supplier,
        wallet=wallet
    )


# ============================================================
# 🟣 مسار حذف الشريك
# ============================================================
@suppliers_bp.route('/<int:supplier_id>/delete', methods=['POST'])
@login_required
def delete_supplier(supplier_id):
    """حذف الشريك (مع حذف المحفظة والربط)."""
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        
        # ✅ حذف المحفظة المرتبطة
        wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
        if wallet:
            db.session.delete(wallet)
        
        # ✅ حذف الربط مع المنتجات
        mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id).all()
        for mapping in mappings:
            db.session.delete(mapping)
        
        # ✅ حذف المورد
        db.session.delete(supplier)
        db.session.commit()
        
        return jsonify({"success": True, "message": "تم حذف الشريك بنجاح."})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================================
# 🟣 مسار تصدير بيانات الشركاء
# ============================================================
@suppliers_bp.route('/export', methods=['GET'])
@login_required
def export_suppliers():
    """تصدير بيانات الشركاء بصيغة CSV."""
    try:
        suppliers = Supplier.query.order_by(Supplier.id.desc()).all()
        
        # ✅ تحويل البيانات إلى CSV
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # ✅ كتابة الرأس
        writer.writerow([
            'ID', 'اسم المتجر', 'اسم المالك', 'كود المورد', 
            'رقم الهاتف', 'الحالة', 'الرتبة', 'تاريخ الانضمام'
        ])
        
        # ✅ كتابة البيانات
        for s in suppliers:
            writer.writerow([
                s.id,
                s.trade_name or s.username,
                s.owner_name or '',
                s.supplier_code or '',
                s.phone or '',
                s.status or '',
                s.rank or '',
                s.created_at.strftime('%Y-%m-%d') if s.created_at else ''
            ])
        
        # ✅ إرجاع الملف
        response = output.getvalue()
        output.close()
        
        return response, 200, {
            'Content-Type': 'text/csv; charset=utf-8',
            'Content-Disposition': f'attachment; filename=suppliers_{datetime.now().strftime("%Y%m%d")}.csv'
        }
        
    except Exception as e:
        flash(f"❌ حدث خطأ أثناء التصدير: {str(e)}", "danger")
        return redirect(url_for('suppliers_bp.list_suppliers'))


# ============================================================
# 🟣 مسار التصفية المالية (SAR فقط)
# ============================================================
@suppliers_bp.route('/settle/<int:supplier_id>', methods=['POST', 'GET'])
@login_required
def settle_supplier_funds(supplier_id):
    """تصفية رصيد المورد (عملة SAR فقط)."""
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    if not wallet:
        flash("خطأ: المحفظة غير موجودة.", "danger")
        return redirect(url_for('suppliers_bp.list_suppliers'))

    # ✅ تصفية الرصيد بالريال السعودي فقط
    wallet.balance_sar = 0
    db.session.commit()
    
    flash("✅ تمت تصفية رصيد المورد بالكامل (SAR)", "success")
    return redirect(url_for('suppliers_bp.list_suppliers'))


# ============================================================
# 🟣 مسار إضافة شريك جديد
# ============================================================
@suppliers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    """إضافة شريك جديد."""
    if request.method == 'POST':
        # سيتم تنفيذ منطق الإضافة هنا
        # حالياً يتم التوجيه إلى صفحة الإضافة المخصصة
        return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))
    
    return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))
