# coding: utf-8
# 🔑 مسارات محرك الموردين المعزول - منصة محجوب أونلاين 2026

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
import jinja2
import secrets

# استيراد البلوبرينت المعتمد والمُعمّد في ملف الـ __init__
from . import admin_suppliers

# هنا نقوم بمحاكاة جلب أو توليد المعرف السيادي المتوقع للمورد الجديد
def generate_sovereign_id():
    """توليد معرف رقمي فريد ومحكم للمورد الجديد"""
    return f"MS-{secrets.randbelow(900000) + 100000}"

@admin_suppliers.route('/add', methods=['GET', 'POST'])
@login_required  # حماية النفاذ السيادي - لا يدخل هنا إلا الإدارة المعمدة
def add_supplier():
    """تعميد وإضافة مورد جديد للنظام الرقمي للمنصة"""
    if request.method == 'POST':
        # استقبال البيانات القادمة من الواجهة الأمامية
        username = request.form.get('username')
        password = request.form.get('password')
        sovereign_id = request.form.get('sovereign_id')
        owner_name = request.form.get('owner_name')
        trade_name = request.form.get('trade_name')
        owner_phone = request.form.get('owner_phone')
        shop_phone = request.form.get('shop_phone')
        province = request.form.get('province')
        district = request.form.get('district')
        address_detail = request.form.get('address_detail')
        bank_name = request.form.get('bank_name')
        bank_acc = request.form.get('bank_acc')
        activity_type = request.form.get('activity_type')
        
        # معالجة رفع الملف (صورة الوثيقة) إن وجدت
        identity_image = request.files.get('identity_image')
        if identity_image and identity_image.filename != '':
            # هنا يمكنك حفظ الصورة في السيرفر أو السحابة لاحقاً
            pass

        # -------------------------------------------------------------
        # 💡 [ملاحظة للمستقبل]: هنا سيتم كتابة كود الحفظ في قاعدة البيانات (SQLAlchemy)
        # -------------------------------------------------------------

        # إرجاع استجابة JSON نجاح لكي تلتقطها الواجهة وتظهر مودال التوثيق
        return jsonify({
            "status": "success",
            "message": "تم تعميد المورد بنجاح في النظام الحوكمي الموحد.",
            "data": {
                "username": username,
                "sovereign_id": sovereign_id
            }
        }), 200

    # في حالة طلب الصفحة (GET): توليد معرف جديد ورندرة الواجهة
    sovereign_id = generate_sovereign_id()
    
    # محاولة قراءة القالب من المجلد الفرعي، وإذا تعذر يقرأه مباشرة منعاً للـ 500
    try:
        return render_template('admin/add_supplier.html', sovereign_id=sovereign_id, owner=current_user)
    except jinja2.exceptions.TemplateNotFound:
        return render_template('add_supplier.html', sovereign_id=sovereign_id, owner=current_user)


@admin_suppliers.route('/check-duplicate', methods=['GET'])
@login_required
def check_duplicate():
    """فحص فوري لمنع تكرار بيانات الوصول أو الهويات في قاعدة البيانات"""
    check_type = request.args.get('type')
    value = request.args.get('value', '').strip()
    
    if not check_type or not value:
        return jsonify({"exists": False}), 400

    # افتراضياً: البيانات غير مكررة وصالحة للاستخدام
    is_duplicate = False

    # -------------------------------------------------------------
    # 💡 [ملاحظة للمستقبل]: هنا سيتم الفحص الفعلي داخل الجداول كالتالي:
    # if check_type == 'username':
    #     is_duplicate = db.session.query(Supplier).filter_by(username=value).exists()
    # -------------------------------------------------------------

    return jsonify({"exists": is_duplicate}), 200
