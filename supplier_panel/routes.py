from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from core.models import Product, Supplier  # استيراد موحد ومنظم

# تعريف البلوبرنت الخاص بالموردين
supplier_bp = Blueprint('supplier_panel', __name__, template_folder='templates')

@supplier_bp.route('/dashboard')
@login_required
def dashboard():
    # التأكد من أن المستخدم لديه صلاحية مورد
    if current_user.role != 'supplier':
        flash('عذراً، هذه المنطقة مخصصة لشركاء الترسانة فقط.', 'danger')
        return redirect(url_for('admin_panel.login'))

    # جلب بيانات متجر المورد الحالي بدون تكرار استعلامات
    supplier_info = Supplier.query.filter_by(user_id=current_user.id).first()
    
    # جلب منتجات هذا المورد فقط لعرضها في الإحصائيات
    my_products = Product.query.filter_by(supplier_id=supplier_info.id).all() if supplier_info else []
    
    return render_template(
        'supplier_panel/dashboard.html', 
        supplier=supplier_info, 
        products_count=len(my_products)
    )

@supplier_bp.route('/logout')
@login_required
def logout():
    # هذا المسار الذي أصلحناه لتجنب الـ BuildError السابق
    from flask_login import logout_user
    logout_user()
    flash('تم تسجيل الخروج من بوابة الموردين بنجاح.', 'success')
    return redirect(url_for('supplier_panel.login'))
