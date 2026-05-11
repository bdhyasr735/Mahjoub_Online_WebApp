# admin_panel/add_supplier_routes.py
from flask import render_template, request, jsonify
from flask_login import login_required
from . import admin_bp
from .engines.supplier_engine import create_new_supplier, get_suppliers_by_filter 
from core.models.supplier import Supplier 

@admin_bp.route('/suppliers/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    """مسار التعميد السيادي للموردين - نسخة الحماية v4.0"""
    if request.method == 'POST':
        try:
            # إرسال البيانات للمحرك المتخصص
            # تأكد من أن المحرك لا ينهار داخلياً
            success, result = create_new_supplier(request.form)
            
            if success:
                return jsonify({
                    "status": "success", 
                    "message": f"تم التعميد بنجاح! المعرف السيادي: {result}"
                })
            else:
                # إرسال الخطأ بتنسيق JSON واضح للواجهة
                return jsonify({
                    "status": "error", 
                    "message": f"فشل التعميد: {result}"
                }), 400 # تغيير الكود من 500 إلى 400 ليكون أكثر دقة

        except Exception as e:
            # خط الدفاع الأخير: منع إرسال صفحة HTML في حالة انهيار الكود
            return jsonify({
                "status": "error",
                "message": f"خطأ غير متوقع في الخادم: {str(e)}"
            }), 500

    # حساب المعرف القادم للعرض في الواجهة (للعرض فقط)
    try:
        last_s = Supplier.query.order_by(Supplier.id.desc()).first()
        next_id = (last_s.id + 1) if last_s else 1
    except:
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
                "trade_name": s.trade_name,
                "owner_name": s.owner_name,
                "province": s.province or "غير محدد",
                "tier": s.tier or "مبتدئ",
                "balance_yer": float(s.balance_yer or 0),
                "balance_sar": float(s.balance_sar or 0),
                "balance_usd": float(s.balance_usd or 0),
                "status": s.status,
                "staff_count": getattr(s, 'staff_count', 0)
            })

        return jsonify(output)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
