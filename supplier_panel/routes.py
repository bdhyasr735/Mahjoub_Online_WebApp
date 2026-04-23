from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from core.models import db, Supplier, User, Wallet, Product
from werkzeug.utils import secure_filename
import os

supplier_bp = Blueprint('supplier', __name__)

@supplier_bp.route('/join', methods=['GET', 'POST'])
def join_request():
    """صفحة طلب انضمام مورد جديد"""
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        
        # معالجة صورة الهوية (الترانزيت المؤقت)
        file = request.files['identity_card']
        if file:
            filename = secure_filename(f"{phone}_{file.filename}")
            filepath = os.path.join('static/img/temp_uploads', filename)
            file.save(filepath)
            
            # إنشاء سجل المورد بحالة "قيد الانتظار"
            new_supplier = Supplier(
                name=name,
                phone_whatsapp=phone,
                identity_url=filepath, # مسار مؤقت حتى التعميد
                status='pending'
            )
            db.session.add(new_supplier)
            db.session.commit()
            
            flash("تم استلام طلبك بنجاح، سيتم التواصل معك عبر الواتساب بعد مراجعة الهوية.")
            return redirect(url_for('supplier.join_request'))
            
    return render_template('supplier/join.html')

@supplier_bp.route('/dashboard')
def dashboard():
    """لوحة تحكم المورد - تختلف حسب الصلاحية"""
    if 'user_id' not in session:
        return redirect(url_for('supplier.login'))
        
    user = User.query.get(session['user_id'])
    supplier = user.supplier
    
    # جلب المنتجات الخاصة بهذا المورد فقط
    my_products = Product.query.filter_by(supplier_id=supplier.id).all()
    
    return render_template('supplier/dashboard.html', 
                           user=user, 
                           supplier=supplier, 
                           products=my_products)

@supplier_bp.route('/wallet')
def wallet():
    """المحفظة المالية - للملاك فقط"""
    if 'user_id' not in session:
        return redirect(url_for('supplier.login'))
        
    user = User.query.get(session['user_id'])
    
    # قيد أمني: إذا كان موظفاً، امنعه من رؤية المحفظة
    if user.role != 'owner':
        flash("عذراً، صلاحية الوصول للمحفظة متاحة للمالك فقط.")
        return redirect(url_for('supplier.dashboard'))
    
    wallet = Wallet.query.filter_by(supplier_id=user.supplier_id).first()
    return render_template('supplier/wallet.html', wallet=wallet)
