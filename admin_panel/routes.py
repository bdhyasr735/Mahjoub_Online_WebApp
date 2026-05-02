from flask import render_template, request, redirect, url_for, flash
# استيراد db من النواة بناءً على ملف core/__init__.py
from core import db 

# تصحيح الاستيراد بناءً على هيكلية core/models/__init__.py
try:
    from core.models import Vendor, User
    # محاولة استيراد WithdrawRequest من الموديلات
    from core.models.vendor import WithdrawRequest
except ImportError:
    # تعريف كلاس وهمي لمنع الانهيار إذا لم يكن الموديل جاهزاً بعد
    WithdrawRequest = None

# استيراد البلوبرنت الخاص بالإدارة
from . import admin_bp

@admin_bp.route('/withdraw-requests')
def withdraw_requests():
    """عرض كافة طلبات تصفية الأرصدة المعلقة للموردين"""
    if WithdrawRequest is None:
        flash("تنبيه: كلاس WithdrawRequest غير معرف في النظام حالياً.", "danger")
        return render_template('withdraw_requests.html', requests=[])
    
    try:
        # جلب الطلبات المعلقة وترتيبها من الأحدث
        pending_requests = WithdrawRequest.query.filter_by(status='pending').order_by(WithdrawRequest.created_at.desc()).all()
        return render_template('withdraw_requests.html', requests=pending_requests)
    except Exception as e:
        flash(f"حدث خطأ أثناء جلب البيانات: {str(e)}", "danger")
        return render_template('withdraw_requests.html', requests=[])

@admin_bp.route('/finalize-withdrawal', methods=['POST'])
def finalize_withdrawal():
    """دالة التعميد المالي لأرشفة بيانات التحويل وتصفية الأرصدة"""
    request_id = request.form.get('request_id')
    bank_name = request.form.get('bank_name')
    reference_number = request.form.get('reference_number')

    if not request_id or not reference_number:
        flash("تنبيه: يجب إدخال رقم الحوالة المرجعي لإتمام عملية التعميد.", "warning")
        return redirect(url_for('admin.withdraw_requests'))

    if WithdrawRequest is None:
        flash("خطأ تقني: نظام السحب غير مفعل.", "danger")
        return redirect(url_for('admin.withdraw_requests'))

    withdrawal_entry = WithdrawRequest.query.get(request_id)

    if not withdrawal_entry:
        flash("خطأ: لم يتم العثور على سجل لهذا الطلب.", "danger")
        return redirect(url_for('admin.withdraw_requests'))

    try:
        # تحديث بيانات السجل المالي للتعميد والأرشفة
        withdrawal_entry.status = 'completed'
        withdrawal_entry.bank_used = bank_name
        withdrawal_entry.reference_id = reference_number
        
        # حفظ التغييرات نهائياً في قاعدة البيانات
        db.session.commit()
        
        flash(f"تم تعميد الحوالة رقم ({reference_number}) بنجاح وأرشفة الطلب.", "success")
        
    except Exception as e:
        db.session.rollback() # التراجع في حالة وجود خلل لضمان سلامة الأرصدة
        flash(f"فشل نظام الأرشفة في معالجة الطلب: {str(e)}", "danger")

    return redirect(url_for('admin.withdraw_requests'))
