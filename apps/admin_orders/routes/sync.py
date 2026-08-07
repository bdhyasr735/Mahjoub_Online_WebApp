# 📂 apps/admin_Orders/routes/sync.py
# مزامنة الطلبات (بناءً على هيكلية مزامنة المنتجات الناجحة)

import functools
import traceback
from flask import request, jsonify, redirect, url_for, flash, session
from flask_login import login_required
from apps.admin_Orders.routes import admin_order_bp
from apps.services import services
from apps.models.order import Order  # عدل اسم المودل حسب مشروعكم

# احتفظ بنفس المزين (Decorator) لتحليل الأخطاء
def analyze_render_error(route_func):
    @functools.wraps(route_func)
    def wrapper(*args, **kwargs):
        try:
            return route_func(*args, **kwargs)
        except Exception as e:
            error_type = type(e).__name__
            error_message = str(e)
            tb_details = traceback.format_exc()
            
            print(f"\n================ 🚨 ORDER SYNC RENDER ERROR ================")
            print(f"📍 الدالة: {route_func.__name__}")
            print(f"🔴 نوع الخطأ: {error_type}")
            print(f"💬 التفاصيل: {error_message}")
            print(f"🛠️ التتبع البرمجي:\n{tb_details}")
            print(f"===========================================================\n")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.method == 'POST':
                return jsonify({"success": False, "message": f"❌ خطأ في النظام: {error_message}"}, 400)
            return jsonify({"success": False, "message": f"❌ خطأ في Render: {error_message}"}, 500)
    return wrapper

@admin_order_bp.route('/orders/sync', methods=['GET', 'POST'])
@login_required
@analyze_render_error
def sync_orders():
    """مزامنة الطلبات مع رصد الأخطاء وإرجاع الإحصائيات"""
    user_type = session.get('user_type')
    if user_type != 'admin':
        return jsonify({'success': False, 'message': 'غير مصرح - صلاحيات مشرف مطلوبة'}), 403

    try:
        # الفرق الجوهري هنا: استدعاء خدمة الطلبات بدلاً من المنتجات
        result = services.orders.get_all_orders() or {}
        external_orders = result.get('data', []) if isinstance(result, dict) else []
        
        if not external_orders:
            return jsonify({
                'success': True,
                'message': 'ℹ️ لا توجد طلبات للمزامنة من المصدر السحابي',
                'syncedCount': 0,
                'createdCount': 0,
                'updatedCount': 0,
                'errors': []
            })
        
        synced_count = len(external_orders)
        created_count = 0
        updated_count = 0
        errors = []
        
        for order in external_orders:
            try:
                if not isinstance(order, dict):
                    continue
                
                order_ref = order.get('order_ref') or order.get('id') # الـ ID الخارجي للطلب
                if not order_ref:
                    continue
                
                # التحقق من وجود الطلب في قاعدة البيانات (بناءً على الـ order_ref)
                existing_order = Order.query.filter_by(external_ref=order_ref).first()
                # أو استخدم Order.query.filter_by(id=order_ref).first() حسب تصميم قاعدة بياناتكم
                
                if not existing_order:
                    # ✅ منطق إنشاء طلب جديد
                    # هنا تقوم بتعبئة الحقول (العميل، التاريخ، المبلغ، الحالة...)
                    # new_order = Order(...)
                    # db.session.add(new_order)
                    created_count += 1
                else:
                    # 🔄 منطق تحديث طلب موجود (مثلاً تحديث الحالة المالية أو حالة الشحن)
                    updated_count += 1
                    
            except Exception as ex:
                errors.append({
                    'order_ref': order.get('order_ref', 'unknown') if isinstance(order, dict) else 'unknown',
                    'error': str(ex)
                })
        
        # مسح كاش البحث للطلبات إذا وجد
        try:
            if hasattr(services.orders, 'clear_search_cache'):
                services.orders.clear_search_cache()
        except Exception as cache_error:
            print(f"⚠️ [Sync Orders]: خطأ في مسح Cache: {cache_error}")
        
        if request.method == 'GET' and request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            flash(f'✅ تمت مزامنة الطلبات: {synced_count} (جديد: {created_count}, محدث: {updated_count})', 'success')
            return redirect(url_for('admin_order_bp.manage_orders_view')) # تأكد من اسم المسار هنا
        
        return jsonify({
            'success': True,
            'message': '✅ تمت مزامنة الطلبات بنجاح.',
            'syncedCount': synced_count,
            'createdCount': created_count,
            'updatedCount': updated_count,
            'errors': errors
        })
        
    except Exception as e:
        print(f"❌ خطأ في sync_orders: {e}")
        return jsonify({'success': False, 'message': f'❌ فشل المزامنة: {str(e)}'}), 400
