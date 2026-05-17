# coding: utf-8
# 🔑 محرك الموردين المطوّر - منصة محجوب أونلاين 2026

from flask import render_template, request, jsonify, current_app
from flask_login import login_required, current_user
import jinja2

# استيراد البلوبرينت المعزول
from . import admin_suppliers
# من أجل جلب موديل الموردين (تأكد من تعديل اسم الموديل وفقاً لما هو لديك في المشروع)
# from apps.models import Supplier  

def generate_sovereign_id():
    """
    سحب آخر رقم مورد من قاعدة البيانات وزيادة العداد المتغير بمقدار 1 تلقائياً.
    النمط المعتمد: الثابت هو SUP-WEL-MAH963 والمتغير هو الرقم الأخير (18 -> 19)
    """
    prefix = "SUP-WEL-MAH963"
    default_id = f"{prefix}19"  # القيمة الافتراضية التالية بعد الرقم 18 الظاهر في قاعدتك
    
    try:
        # 💡 استعلام جلب آخر مورد مضاف لقاعدة البيانات
        # last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
        last_supplier = None  # (قم بإلغاء تعليق السطر الأعلى عند ربطه بالموديل الحقيقي)
        
        if last_supplier and last_supplier.sovereign_id:
            last_code = last_supplier.sovereign_id.strip()
            
            # التحقق من أن الكود يبدأ بالجزء الثابت
            if last_code.startswith(prefix):
                # استخراج الجزء الرقمي المتغير (ما بعد الـ 963)
                num_part_str = last_code.replace(prefix, "")
                if num_part_str.isdigit():
                    next_num = int(num_part_str) + 1
                    # إرجاع المعرف الجديد مدمجاً مع الجزء الثابت
                    return f"{prefix}{next_num}"
    except Exception as e:
        current_app.logger.error(f"❌ خطأ أثناء احتساب الرقم الحوكمي التالي: {str(e)}")
    
    return default_id


@admin_suppliers.route('/add', methods=['GET', 'POST'], endpoint='add_supplier_page')
@admin_suppliers.route('/add_legacy', methods=['GET', 'POST'], endpoint='add_supplier')
@login_required
def add_supplier_page():
    if request.method == 'POST':
        username = request.form.get('username')
        sovereign_id = request.form.get('sovereign_id')
        trade_name = request.form.get('trade_name')
        owner_phone = request.form.get('owner_phone')
        
        # [منطق حفظ البيانات في الـ DB]
        
        return jsonify({
            "status": "success",
            "message": "تم تعميد الشريك بنجاح في النظام الحوكمي."
        }), 200

    # توليد المعرف المتوقع ديناميكياً بناءً على آخر رقم + 1
    sovereign_id = generate_sovereign_id()
    
    try:
        return render_template('admin/add_supplier.html', sovereign_id=sovereign_id, owner=current_user)
    except jinja2.exceptions.TemplateNotFound:
        return render_template('add_supplier.html', sovereign_id=sovereign_id, owner=current_user)


@admin_suppliers.route('/check-duplicate', methods=['GET'])
@login_required
def check_duplicate():
    """
    الفحص اللحظي لمنع التكرار البنيوي أثناء كتابة المورد للبيانات
    """
    check_type = request.args.get('type')
    value = request.args.get('value', '').strip()
    
    if not check_type or not value:
        return jsonify({"exists": False}), 400
        
    exists = False
    try:
        # [منطق فحص التكرار من قاعدة البيانات]
        # if check_type == 'username':
        #     exists = Supplier.query.filter_by(username=value).first() is not None
        pass
    except Exception as e:
        current_app.logger.error(f"خطأ في فحص التكرار: {str(e)}")
        
    return jsonify({"exists": exists})
