# 📂 apps/admin_suppliers_list/routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required
from apps.models import Supplier  # الاستيراد من الواجهة الموحدة
from apps.extensions import db

# تعريف البلوبرينت
# ملاحظة: تمت إزالة url_prefix من هنا لأننا نحدده في registry.py عند تسجيل الموديول
suppliers_bp = Blueprint(
    'suppliers_bp', 
    __name__, 
    template_folder='templates'
)

@suppliers_bp.route('/list', methods=['GET'])
@login_required
def list_suppliers():
    """عرض قائمة الموردين/الشركاء في المنصة."""
    try:
        # جلب جميع الموردين مرتبين حسب الأحدث
        suppliers = Supplier.query.order_by(Supplier.created_at.desc()).all()
    except Exception as e:
        suppliers = []
        # استخدام نظام السجلات الخاص بـ Flask بدلاً من print
        current_app.logger.error(f"⚠️ خطأ أثناء جلب الموردين: {e}")
    
    return render_template(
        'admin_suppliers_list/admin_suppliers_list.html', 
        suppliers=suppliers
    )

@suppliers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    """صفحة إضافة مورد جديد ومعالجة البيانات المرسلة."""
    if request.method == 'POST':
        # استخراج البيانات من النموذج (استبدل 'name' بأسماء الحقول الفعلية لديك)
        name = request.form.get('name')
        
        # تحقق مبدئي من صحة البيانات
        if not name:
            flash("الرجاء إدخال اسم المورد.", "warning")
            return redirect(url_for('suppliers_bp.add_supplier'))
            
        try:
            # إنشاء كائن جديد وحفظه في قاعدة البيانات
            new_supplier = Supplier(name=name)
            db.session.add(new_supplier)
            db.session.commit()
            
            flash("تم إضافة المورد بنجاح!", "success")
            return redirect(url_for('suppliers_bp.list_suppliers'))
            
        except Exception as e:
            db.session.rollback() # التراجع عن المعاملة في حال حدوث خطأ
            current_app.logger.error(f"⚠️ خطأ أثناء إضافة المورد: {e}")
            flash("حدث خطأ أثناء حفظ بيانات المورد.", "danger")

    return render_template('admin_suppliers_list/add.html')

@suppliers_bp.route('/<int:supplier_id>/details', methods=['GET'])
@login_required
def supplier_details(supplier_id):
    """عرض تفاصيل مورد معين."""
    try:
        # استخدام get بدلاً من get_or_404 لتجنب التقاط خطأ 404 بواسطة except Exception
        supplier = Supplier.query.get(supplier_id)
        
        if not supplier:
            flash("المورد المطلوب غير موجود أو تم حذفه.", "warning")
            return redirect(url_for('suppliers_bp.list_suppliers'))
            
        return render_template('admin_suppliers_list/details.html', supplier=supplier)
        
    except Exception as e:
        current_app.logger.error(f"⚠️ خطأ أثناء عرض تفاصيل المورد {supplier_id}: {e}")
        flash("حدث خطأ أثناء جلب تفاصيل المورد.", "danger")
        return redirect(url_for('suppliers_bp.list_suppliers'))
