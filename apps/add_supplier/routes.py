# coding: utf-8
# 🔑 محرك الموردين الحوكمي والسيادي المطور - منصة محجوب أونلاين 2026

from flask import render_template, request, jsonify, current_app, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
import jinja2
import re  # مكتبة التعبيرات النمطية لمعالجة النصوص واستخراج الأرقام بدقة
import random # لتوليد كود رقمي آمن ومميز للمحافظ
from textwrap import dedent

# استيراد البلوبرينت المعزول الخاص بالموردين وكائن قاعدة البيانات
from . import admin_suppliers
from apps import db
from apps.models import Supplier  

def get_expected_sovereign_id():
    """
    سحب آخر معرف سيادي مسجل في قاعدة البيانات بدقة من خلال قراءة الجزء الرقمي 
    الأخير وزيادته بمقدار 1، ليعرض للمسؤول في الواجهة المعرف المتوقع تماماً.
    """
    default_prefix = "SUP-WEL-MAH"
    try:
        last_supplier = db.session.query(Supplier.id, Supplier.sovereign_id)\
                                  .order_by(Supplier.id.desc())\
                                  .first()
        
        if last_supplier and last_supplier.sovereign_id:
            sovereign_str = last_supplier.sovereign_id.strip()
            match = re.search(r'\d+$', sovereign_str)
            if match:
                last_num = int(match.group())
                next_num = last_num + 1
                prefix_match = re.match(r'^(.*?)(\d+)$', sovereign_str)
                if prefix_match:
                    return f"{prefix_match.group(1)}{next_num}"
                return f"{default_prefix}{next_num}"
        
        if last_supplier:
            return f"{default_prefix}96338"

    except Exception as e:
        current_app.logger.error(f"❌ خطأ أثناء احتساب المعرف السيادي القادم: {str(e)}")
    
    return f"{default_prefix}96338"


@admin_suppliers.route('/add', methods=['GET', 'POST'], endpoint='add_supplier_page')
@admin_suppliers.route('/add_legacy', methods=['GET', 'POST'], endpoint='add_supplier')
@login_required
def add_supplier_page():
    if request.method == 'POST':
        try:
            # 1. استقبال البيانات السبعة وعمل تطهير (strip) فوري
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            identity_type = request.form.get('identity_type', '').strip()
            identity_number = request.form.get('identity_number', '').strip()
            owner_name = request.form.get('owner_name', '').strip()
            trade_name = request.form.get('trade_name', '').strip()
            owner_phone = request.form.get('owner_phone', '').strip()
            shop_phone = request.form.get('shop_phone', '').strip()
            province = request.form.get('province', '').strip()
            district = request.form.get('district', '').strip()
            address_detail = request.form.get('address_detail', '').strip()
            fin_type = request.form.get('fin_type', '').strip()
            bank_name = request.form.get('bank_name', '').strip()
            bank_acc = request.form.get('bank_acc', '').strip()
            activity_type = request.form.get('activity_type', '').strip()

            user_rank = request.form.get('user_rank', 'ريادي').strip()
            system_status = 'active'

            # التحقق الفوري الحوكمي من عدم إرسال حقول أساسية فارغة
            required_post_fields = {
                "username": username, "identity_number": identity_number, 
                "owner_name": owner_name, "trade_name": trade_name, 
                "owner_phone": owner_phone, "shop_phone": shop_phone, "bank_acc": bank_acc
            }
            for f_key, f_val in required_post_fields.items():
                if not f_val:
                    return jsonify({
                        "status": "error",
                        "message": f"تنبيه سيادي: لا يمكن تعميد المورد والحقل الأساسي ({f_key}) فارغ."
                    }), 400

            # 2. فحص الحقول السبعة في قاعدة البيانات لمنع تجاوز التكرار
            check_fields = {
                "username": (db.session.query(Supplier.id).filter_by(username=username).first(), "اسم المستخدم (Login)"),
                "identity_number": (db.session.query(Supplier.id).filter_by(identity_number=identity_number).first(), "رقم الوثيقة / الهوية"),
                "owner_name": (db.session.query(Supplier.id).filter_by(owner_name=owner_name).first(), "اسم المالك الكامل"),
                "trade_name": (db.session.query(Supplier.id).filter_by(trade_name=trade_name).first(), "الاسم التجاري للمنشأة"),
                "owner_phone": (db.session.query(Supplier.id).filter_by(owner_phone=owner_phone).first(), "رقم هاتف المالك"),
                "shop_phone": (db.session.query(Supplier.id).filter_by(shop_phone=shop_phone).first(), "هاتف المنشأة (محل)"),
                "bank_acc": (db.session.query(Supplier.id).filter_by(bank_acc=bank_acc).first(), "رقم الحساب")
            }

            for key, (exists, field_title) in check_fields.items():
                if exists:
                    return jsonify({
                        "status": "error",
                        "message": f"تنبيه حوكمي: حقل ({field_title}) مسجل مسبقاً في النظام ومحفوظ، يرجى تعديله."
                    }), 400

            # 3. تشفير كلمة المرور وبناء كائن المورد
            hashed_password = generate_password_hash(password)
            
            new_supplier = Supplier(
                username=username,
                password_hash=hashed_password,
                identity_type=identity_type,
                identity_number=identity_number,
                owner_name=owner_name,
                trade_name=trade_name,
                owner_phone=owner_phone,
                shop_phone=shop_phone,
                province=province,
                district=district,
                address_detail=address_detail,
                fin_type=fin_type,
                bank_name=bank_name,
                bank_acc=bank_acc,
                activity_type=activity_type,
                registration_source='لوحة التحكم',
                rank_grade=user_rank,         
                status=system_status,         
                created_by_id=current_user.id if hasattr(current_user, 'id') else None
            )

            # 4. تعميد المورد مؤقتاً لتوليد الـ ID
            db.session.add(new_supplier)
            db.session.flush()  

            # 5. 💳 محرك توليد المحفظة النقي والمختصر (يمرر فقط الحقول الحاكمة والمؤكدة في قاعدة البيانات)
            generated_wallet_code = f"WLT-{username.upper()}-{random.randint(1000, 9999)}"
            
            insert_query = db.text(dedent("""
                INSERT INTO supplier_wallets (
                    supplier_id, 
                    wallet_code
                ) VALUES (
                    :supplier_id, 
                    :wallet_code
                )
            """))

            db.session.execute(insert_query, {
                "supplier_id": new_supplier.id,
                "wallet_code": generated_wallet_code
            })

            # 6. تثبيت وحفظ العملية التبادلية بالكامل دفعة واحدة
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "تم تعميد المورد وتنشيطه بنجاح وتوليد محفظته المالية الموحدة في النظام الحوكمي السيادي.",
                "data": {
                    "username": new_supplier.username,
                    "sovereign_id": new_supplier.sovereign_id if hasattr(new_supplier, 'sovereign_id') else username,
                    "rank_grade": new_supplier.rank_grade,
                    "state_title": 'نشط'
                }
            }), 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"❌ خطأ بنيوي أثناء حفظ المورد: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"حدث خطأ غير متوقع في قاعدة البيانات: {str(e)}"
            }), 500

    # مرحلة الـ GET لعرض واجهة الإدخال
    sovereign_id = get_expected_sovereign_id()
    csrf_val = ""
    try:
        if 'csrf' in current_app.extensions:
            from flask_wtf.csrf import generate_csrf
            csrf_val = generate_csrf()
    except Exception:
        pass

    try:
        return render_template('admin/add_supplier.html', sovereign_id=sovereign_id, owner=current_user, backup_csrf=csrf_val)
    except jinja2.exceptions.TemplateNotFound:
        return render_template('add_supplier.html', sovereign_id=sovereign_id, owner=current_user, backup_csrf=csrf_val)
