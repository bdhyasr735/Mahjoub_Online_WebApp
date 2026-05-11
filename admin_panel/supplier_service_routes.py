# admin_panel/supplier_service_routes.py
from flask import render_template, request, jsonify
from flask_login import login_required
from admin_panel import admin_bp
from core.models.supplier import Supplier

@admin_bp.route('/suppliers/profile/<int:supplier_id>', methods=['GET', 'POST'])
@login_required
def supplier_profile(supplier_id):
    """
    مسار إدارة بروفايل المورد:
    - GET: عرض بيانات المورد الحالية في الواجهة.
    - POST: استقبال طلبات التحديث وتعميدها عبر المحرك المستقل.
    """
    
    # 1. بروتوكول التحديث (POST) القادم من AJAX
    if request.method == 'POST':
        # استدعاء المحرك هنا داخلياً لكسر دائرة الاستيراد (Circular Import Prevention)
        from core.services.supplier_service import update_supplier_profile
        
        try:
            # استخراج البيانات من الفورم القادم عبر الطلب
            data = request.form.to_dict()
            
            # تنفيذ عملية التعميد في قاعدة البيانات
            success, message = update_supplier_profile(supplier_id, data)
            
            if success:
                return jsonify({
                    "status": "success", 
                    "message": "تم تعميد التحديثات بنجاح في السجلات السيادية."
                })
            else:
                return jsonify({
                    "status": "error", 
                    "message": f"فشل التعميد: {message}"
                }), 400
                
        except Exception as e:
            return jsonify({
                "status": "error", 
                "message": f"خطأ في الاتصال بالمحرك: {str(e)}"
            }), 500

    # 2. بروتوكول العرض (GET)
    # جلب بيانات الكيان أو إظهار 404 في حال عدم الوجود
    supplier = Supplier.query.get_or_404(supplier_id)
    
    return render_template(
        'suppliers/supplier_profile.html', 
        supplier=supplier
    )
