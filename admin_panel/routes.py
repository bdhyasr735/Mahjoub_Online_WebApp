# admin_panel/routes.py
from flask import render_template, redirect, url_for, request, jsonify, flash
from flask_login import login_required, logout_user
from . import admin_bp

# استدعاء الخدمات (النظام المنفصل - الترسانة التقنية)
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
    """ استدعاء الإحصائيات الشاملة من محرك الإحصائيات لعرضها في الرادار """
    try:
        stats = get_admin_dashboard_stats()
        return render_template('admin/dashboard.html', **stats)
    except Exception as e:
        # بروتوكول الطوارئ: تأمين اللوحة في حال فشل الاستعلامات المباشرة
        return render_template('admin/dashboard.html', 
                               error=str(e), 
                               users_count=0, 
                               suppliers_count=0,
                               total_yer=0.0,
                               total_sar=0.0,
                               total_usd=0.0)

# ==========================================
# 3. إدارة الموردين (القائمة السيادية)
# ==========================================
@admin_bp.route('/suppliers')
@login_required
def manage_suppliers():
    """ جلب قائمة الموردين المعتمدين وإحصائيات الرتب من الخدمة المختصة """
    try:
        data = get_all_suppliers()
        # نمرر البيانات للقالب (suppliers و stats) المسترجعة من المحرك
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
    """ معالجة بروتوكول الإرسال والتعميد والأرشفة الرقمية """
    if request.method == 'POST':
        # الحماية من خطأ 415: معالجة البيانات سواء كانت JSON أو Form
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        if not data:
            return jsonify({"status": "error", "message": "عذراً، لم يتم استلام بيانات صالحة للتعميد."}), 400
            
        # استدعاء خدمة الإنشاء (التي تتولى التشفير وتوليد الأكواد SUP-MHA)
        success, result = create_supplier(data)
        
        if success:
            return jsonify({
                "status": "success", 
                "message": f"تم التعميد بنجاح للمورد: {result}"
            })
        
        # بروتوكول الفشل: إرجاع رسالة الخطأ التقنية للمسؤول
        return jsonify({"status": "error", "message": result}), 500

    # في حالة الـ GET: نجهز واجهة الإضافة ونعرض المعرف السيادي القادم
    try:
        next_id = get_next_supplier_id()
    except:
        next_id = "جاري الحساب..."
        
    return render_template('admin/add_supplier.html', next_id=next_id)

# ==========================================
# 5. بروتوكول الخروج الآمن (Logout)
# ==========================================
@admin_bp.route('/logout')
@login_required
def logout():
    """ إنهاء الجلسة وإعادة تشغيل وضع الحماية """
    logout_user()
    flash("تم تسجيل الخروج. النظام في وضع الحماية الآن.", "info")
    return redirect(url_for('admin.login'))

@admin_bp.route('/suppliers/profile/<int:supplier_id>')
@login_required
def supplier_profile(supplier_id):
    from core.models.supplier import Supplier
    try:
        # جلب المورد
        supplier = Supplier.query.get_or_404(supplier_id)
        
        # ملاحظة: تأكد أن الموديل يحتوي على sovereign_id وليس mint_sovereign_id
        return render_template('suppliers/supplier_profile.html', supplier=supplier)
        
    except Exception as e:
        # تسجيل الخطأ في حالة فشل قاعدة البيانات
        print(f"Error accessing supplier {supplier_id}: {str(e)}")
        return "حدث خطأ في الاتصال بقاعدة البيانات السيادية", 500
