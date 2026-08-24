@whatsapp_bp.route('/settings', methods=['GET'])
@login_required
def settings_dashboard():
    """عرض صفحة إعدادات ربط Meta WhatsApp API مع جلب القيم تلقائياً من متغيرات البيئة"""
    try:
        class SettingsObj:
            phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
            business_account_id = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
            api_version = os.getenv("WHATSAPP_API_VERSION", "v21.0")
            access_token = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
            verify_token = WEBHOOK_VERIFY_TOKEN
            updated_at = None

        settings = SettingsObj()
        is_connected = bool(settings.access_token and settings.phone_number_id)

        return render_template(
            'admin/whatsapp_dashboard.html',
            active_tab='settings',
            settings=settings,
            is_connected=is_connected
        )
    except Exception as e:
        flash(f"حدث خطأ أثناء تحميل صفحة الإعدادات: {str(e)}", "danger")
        return redirect(url_for('whatsapp_service.chat_dashboard'))
