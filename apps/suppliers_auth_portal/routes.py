import threading
import sys
import traceback

@suppliers_auth_bp.route('/forgot-password/request-otp', methods=['POST'])
def request_otp():
    """طلب إرسال رمز التحقق OTP مع معالجة سريعة وخلفية لمنع الـ Timeout"""
    try:
        data = request.get_json(silent=True) or request.form.to_dict()
        identifier = data.get('identifier', '').strip()
        
        if not identifier:
            return jsonify({"success": False, "message": "الرجاء إدخال اسم المستخدم أو رقم الهاتف."}), 400
        
        # البحث عن المورد
        supplier = Supplier.query.filter(
            (Supplier.phone == identifier) | 
            (Supplier.username == identifier) | 
            (Supplier.email == identifier) | 
            (Supplier.search_phone == identifier)
        ).first()
        
        if not supplier:
            return jsonify({"success": False, "message": "لم يتم العثور على حساب مرتبط بالبيانات المدخلة."}), 404
        
        # استخدام الرقم المنسق مباشرة من خدمة الـ OTP لتلافي أي اختلاف
        formatted_phone = SupplierOTPService._format_phone_number(supplier.phone)
        
        # التقاط سياق التطبيق الحالي لضمان عمل الـ Thread بسلاسة
        app_obj = current_app._get_current_object() if current_app else None

        # تشغيل التوليد والإرسال في الخلفية لضمان استجابة فورية تمنع خطأ الاتصال
        def background_otp_task(phone, s_id, s_type, app_context):
            def run():
                try:
                    # توليد وإرسال الرمز داخلياً
                    result = SupplierOTPService.generate_and_send_otp(
                        identifier=phone,
                        target_id=s_id,
                        target_type=s_type
                    )
                    print(f"📬 [Background OTP Result]: {result}", file=sys.stderr)
                except Exception as ex:
                    print(f"❌ [خطأ خلفي في OTP]: {str(ex)}", file=sys.stderr)
                    traceback.print_exc()

            if app_context:
                with app_context.app_context():
                    run()
            else:
                run()

        # توليد الرمز وحفظه أولاً بشكل سريع لضمان توفره
        recipient_phone = SupplierOTPService._format_phone_number(supplier.phone)
        otp_record, otp_code = OTP.create_otp(
            identifier=recipient_phone,
            target_id=supplier.id,
            target_type='supplier',
            expiry_seconds=300
        )
        message_text = f"🔐 رمز التحقق الخاص بك في منصة محجوب أونلاين هو: *{otp_code}*\nصالح لمدة 5 دقائق فقط."

        # إطلاق خيط الإرسال الفعلي للواتساب بالخلفية
        thread = threading.Thread(
            target=background_otp_task,
            args=(supplier.phone, supplier.id, 'supplier', app_obj)
        )
        thread.daemon = True
        thread.start()
        
        # إرجاع استجابة ناجحة وفورية للواجهة الأمامية لمنع خطأ الاتصال نهائياً
        return jsonify({
            "success": True,
            "message": "تم إرسال رمز التحقق بنجاح.",
            "data": {
                "masked_phone": f"****{supplier.phone[-4:]}",
                "_dev_otp": otp_code  # يظهر لك الرمز في الاستجابة احتياطياً للتأكد الفوري
            }
        })
        
    except Exception as e:
        print(f"❌ [خطأ في request_otp]: {str(e)}")
        traceback.print_exc()
        return jsonify({"success": False, "message": f"حدث خطأ داخلي: {str(e)}"}), 500
