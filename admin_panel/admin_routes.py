from flask import Blueprint, render_template, request, redirect, url_for, flash
from core.models import db, Supplier, Product, Wallet
from core.qumra_connector import QumraEngine

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
def dashboard():
    """لوحة المعلومات الرئيسية للإدارة"""
    pending_suppliers = Supplier.query.filter_by(status='pending').count()
    total_products = Product.query.count()
    # حساب إجمالي الديون للموردين (Confirmed Balance)
    total_debts = db.session.query(db.func.sum(Wallet.balance_confirmed)).scalar() or 0
    return render_template('admin/dashboard.html', 
                           pending_count=pending_suppliers, 
                           products_count=total_products,
                           debts=total_debts)

@admin_bp.route('/approve_suppliers')
def approve_suppliers():
    """عرض طلبات الانضمام المعلقة"""
    suppliers = Supplier.query.filter_by(status='pending').all()
    return render_template('admin/suppliers_review.html', suppliers=suppliers)

@admin_bp.route('/verify_supplier/<int:id>', methods=['POST'])
def verify_supplier(id):
    """تعميد المورد وإنشاء محفظته فوراً"""
    supplier = Supplier.query.get_or_404(id)
    action = request.form.get('action') # 'approve' or 'reject'
    
    if action == 'approve':
        supplier.status = 'active'
        # إنشاء المحفظة تلقائياً عند التفعيل
        if not supplier.wallet:
            new_wallet = Wallet(supplier_id=supplier.id)
            db.session.add(new_wallet)
        db.session.commit()
        # هنا سيتم استدعاء كود إرسال الواتساب للمورد لاحقاً
        flash(f"تم اعتماد المورد {supplier.name} بنجاح")
    return redirect(url_for('admin.approve_suppliers'))

@admin_bp.route('/sync_products')
def sync_products():
    """سحب المنتجات الجديدة من قمرة لعرضها للتعميد"""
    external_products = QumraEngine.fetch_products()
    return render_template('admin/sync_products.html', products=external_products)

@admin_bp.route('/finalize_product', methods=['POST'])
def finalize_product():
    """اعتماد المنتج النهائي وتحديد سعر البيع"""
    # هذا الكود يستقبل التكلفة (يمني) وسعر البيع (سعودي)
    # ويقوم بحساب الربح وتخزينه في جدول المنتجات
    qumra_id = request.form.get('qumra_id')
    cost_yem = float(request.form.get('cost_yem'))
    price_sar = float(request.form.get('price_sar'))
    
    product = Product(
        qumra_id=qumra_id,
        cost_yemeni=cost_yem,
        price_saudi=price_sar,
        approval_status='approved'
    )
    db.session.add(product)
    db.session.commit()
    flash("تم تعميد المنتج ونشره بنجاح")
    return redirect(url_for('admin.sync_products'))
