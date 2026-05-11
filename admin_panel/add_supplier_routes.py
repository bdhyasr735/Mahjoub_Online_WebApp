# admin_panel/add_supplier_routes.py
from flask import render_template, request, jsonify, current_app
from flask_login import login_required
from . import admin_bp
from .engines.supplier_engine import create_new_supplier, get_suppliers_by_filter
from core.models.supplier import Supplier

@admin_bp.route('/suppliers/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    """مسار التعميد السيادي للموردين - نسخة الاستقرار v5.0"""
    if request.method == 'POST':
        try:
            # التحقق من المدخلات الأساسية قبل تمريرها للمحرك
            trade_name = request.form.get("trade_name")
            email = request.form.get("email")

            if not trade_name or not email:
                return jsonify({
                    "status": "error",
                    "message": "اسم المورد والبريد الإلكتروني مطلوبان"
                }), 400

            # تمرير البيانات للمحرك
            success, result = create_new_supplier(request.form)

            if success:
                return jsonify({
                    "status": "success",
                    "message": f"تم التعميد بنجاح! المعرف السيادي: {result}"
                }), 201
            else:
                return jsonify({
                    "status": "error",
                    "message": f"فشل التعميد: {result}"
                }), 400

        except Exception as e:
            # تسجيل الخطأ في سجل التطبيق
            current_app.logger.error(f"عطل غير متوقع في البوابة: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "حدث خطأ غير متوقع أثناء التعميد"
            }), 500

    # حساب المعرف القادم للعرض فقط
    try:
        last_s = Supplier.query.order_by(Supplier.id.desc()).first()
        next_id = (last_s.id + 1) if last_s else 1
    except Exception as e:
        current_app.logger.warning(f"تعذر حساب المعرف القادم: {str(e)}")
        next_id = "تلقائي"

    return render_template('admin/add_supplier.html', next_id=next_id)


@admin_bp.route('/api/suppliers/search', methods=['GET'])
@login_required
def search_suppliers_api():
    """نقطة الوصول الذكية: تجلب البيانات المفلترة بتنسيق JSON آمن"""
    try:
        query_text = request.args.get('q', '').strip()
        province = request.args.get('province', '')
        status = request.args.get('status', '')

        suppliers = get_suppliers_by_filter(
            query_text=query_text,
            province=province,
            status=status,
            limit=10
        )

        output = []
        for s in suppliers:
            output.append({
                "id": s.id,
                "sovereign_id": s.sovereign_id or f"SUP_{s.id}#",
                "trade_name": s.trade_name or "غير محدد",
                "owner_name": s.owner_name or "غير محدد",
                "province": s.province or "غير محدد",
                "tier": s.tier or "مبتدئ",
                "balance_yer": float(s.balance_yer or 0),
                "balance_sar": float(s.balance_sar or 0),
                "balance_usd": float(s.balance_usd or 0),
                "status": s.status or "غير محدد",
                "staff_count": getattr(s, 'staff_count', 0)
            })

        return jsonify(output), 200

    except Exception as e:
        current_app.logger.error(f"خطأ أثناء البحث عن الموردين: {str(e)}")
        return jsonify({"error": "حدث خطأ غير متوقع أثناء البحث"}), 500
