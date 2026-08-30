from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash
# استيراد نموذج قاعدة البيانات والاتصال الخاص بك (على سبيل المثال db و Supplier)
# from models import db, Supplier

auth_bp = Blueprint('suppliers_auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "بيانات الطلب غير صالحة."
            }), 400

        company_name = data.get('company_name', '').strip()
        contact_person = data.get('contact_person', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        category = data.get('category', '').strip()
        agree_pricing_policy = data.get('agree_pricing_policy', False)

        # التحقق من الحقول الإجبارية
        if not company_name or not contact_person or not phone or not password or not category:
            return jsonify({
                "success": False,
                "message": "يرجى تعبئة كافة الحقول الإجبارية المميزة بنجمة."
            }), 400

        # التحقق من الموافقة على سياسة حوكمة الأسعار
        if not agree_pricing_policy:
            return jsonify({
                "success": False,
                "message": "يجب الموافقة على شروط حوكمة التوريد والأسعار بسعر التكلفة للاستمرار."
            }), 400

        # التحقق من عدم تكرار رقم الهاتف أو البريد الإلكتروني مسبقاً
        # existing_supplier = Supplier.query.filter((Supplier.phone == phone) | (Supplier.email == email)).first()
        # if existing_supplier:
        #     return jsonify({
        #         "success": False,
        #         "message": "رقم الهاتف أو البريد الإلكتروني مسجل مسبقاً في النظام."
        #     }), 400

        # تشفير كلمة المرور وتشييد حساب المورد الجديد
        hashed_password = generate_password_hash(password)
        
        # new_supplier = Supplier(
        #     company_name=company_name,
        #     contact_person=contact_person,
        #     phone=phone,
        #     email=email if email else None,
        #     password_hash=hashed_password,
        #     category=category,
        #     agree_pricing_policy=True,
        #     is_active=True
        # )
        # db.session.add(new_supplier)
        # db.session.commit()

        # تسجيل الدخول تلقائياً عبر جلسة المستخدم (Session)
        # session['supplier_id'] = new_supplier.id
        # session['company_name'] = new_supplier.company_name

        return jsonify({
            "success": True,
            "message": "تم إنشاء الحساب بنجاح.",
            "redirect_url": "/supplier/dashboard"
        }), 200

    except Exception as e:
        # تسجيل الخطأ داخلياً إذا لزم الأمر
        return jsonify({
            "success": False,
            "message": f"حدث خطأ غير متوقع في الخادم: {str(e)}"
        }), 500
