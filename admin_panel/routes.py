# admin_panel/routes.py
from flask import render_template, redirect, url_for, request, jsonify, flash
from flask_login import login_required, logout_user
from . import admin_bp

# 🛡️ استدعاء الخدمات السيادية (الترسانة التقنية)
# ملاحظة: استدعاء دالة التعديل supplier_profile يتم عبر الملف المنفصل supplier_service_routes.py
from core.services.supplier_service import get_all_suppliers, create_supplier, get_next_supplier_id
from core.services.stats_service import get_admin_dashboard_stats
from .auth import login_view 

# ==========================================
# 1. بوابة الولوج (The Login Gate)
# ==========================================
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """ استدعاء واجهة تسجيل الدخول المنفصلة لضمان أمن النظام """
    return login_view()

# ==========================================
# 2. غرفة القيادة (Dashboard)
# ==========================================
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """ عرض الرادار الشامل والإحصائيات الحية للكيانات """
    try:
        stats = get_admin_dashboard_stats()
        return render_template('admin/dashboard.html', **stats)
    except Exception as e:
        # بروتوكول الطوارئ: تأمين اللوحة بالقيم الصفرية في حال تعثر المحرك
        return render_template('admin/dashboard.html', 
                               error=str(e), 
                               users_count=0, 
                               suppliers_count=0,
                               total_yer=0.0,
                               total_sar=0.0,
                               total_usd=0.0)

# ==========================================
# 3. رادار الموردين (القائمة السيادية)
# ==========================================
@admin_bp.route('/suppliers')
@login_required
def manage_suppliers():
    """ عرض قائمة الكيانات المعتمدة وإحصائيات الرتب """
    try:
        data = get_all_suppliers()
        return render_template('admin/manage_suppliers.html', **data)
    except Exception as e:
        flash(f"⚠️ عطل في رادار الموردين: {str(e)}", "danger")
        return redirect(url_for('admin.dashboard'))

# ==========================================
# 4. تعميد مورد جديد (Add Supplier)
# ==========================================
@admin_bp.route('/suppliers/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    """ معالجة بروتوكول الإرسال والتعميد والأرشفة الرقمية لمورد جديد """
    if request.method == 'POST':
        # استقبال البيانات سواء كانت JSON أو Form
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        if not data:
            return jsonify({"status": "error", "message": "لم يتم استلام بيانات صالحة للتعميد."}), 400
            
        # تنفيذ عملية الإنشاء عبر الخدمة المختصة
        success, result = create_supplier(data)
        
        if success:
            return jsonify({
                "status": "success", 
                "message": f"تم تعميد المورد بنجاح: {result}"
            })
        
        return jsonify({"status": "error", "message": result}), 500

    # في حالة العرض: جلب الرقم التسلسلي القادم تلقائياً
    next_id = get_next_supplier_id()
    return render_template('admin/add_supplier.html', next_id=next_id)

# ==========================================
# 5. بروتوكول الخروج الآمن (Logout)
# ==========================================
@admin_bp.route('/logout')
@login_required
def logout():
    """ إنهاء الجلسة وإعادة تشغيل وضع الحماية """
    logout_user()
    flash("تم تسجيل الخروج بنجاح. النظام الآن تحت الحماية.", "info")
    return redirect(url_for('admin.login'))

"""
--- توثيق الاستقرار (القائد علي محجوب) ---
- تم فصل مسار 'supplier_profile' ليكون في 'supplier_service_routes.py'.
- تم ربط كافة المسارات بالخدمات (Services) لضمان Clean Architecture.
- النظام جاهز للنشر (Deployment) على Railway بدون تداخلات.
"""
