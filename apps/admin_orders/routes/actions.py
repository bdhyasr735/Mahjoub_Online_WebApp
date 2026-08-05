# 📂 apps/admin_orders/routes/actions.py
from flask import Blueprint, request, jsonify, current_app
from apps.extensions import db

# إنشاء الـ Blueprint الخاص بأفعال وعمليات الطلبات
actions_bp = Blueprint('admin_orders_actions', __name__)


@actions_bp.route('/admin/orders/<order_id>/update-status', methods=['POST'])
def update_order_status(order_id):
    """
    استقبال طلب تحديث حالة الطلب من الواجهة وتغييرها في قاعدة البيانات
    """
    try:
        data = request.get_json() or {}
        new_status = data.get('status')

        if not new_status:
            return jsonify({'success': False, 'message': 'حالة الطلب غير محددة'}), 400

        # 1. تحديث حالة الطلب مباشر في قاعدة البيانات
        db.session.execute(
            db.text("UPDATE orders SET status = :status WHERE id = :order_id"),
            {'status': new_status, 'order_id': order_id}
        )
        db.session.commit()

        # 2. توثيق الحركة في سجل المراجعة (Audit Log)
        _record_audit_log(
            action='UPDATE_ORDER_STATUS',
            details=f'تم تغيير حالة الطلب #{order_id} إلى: {new_status}'
        )

        return jsonify({
            'success': True,
            'message': 'تم تحديث حالة الطلب بنجاح',
            'status': new_status
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating order {order_id} status: {str(e)}")
        return jsonify({'success': False, 'message': f'حدث خطأ أثناء التحديث: {str(e)}'}), 500


@actions_bp.route('/admin/orders/<order_id>/item/<item_id>/assign-supplier', methods=['POST'])
def assign_item_supplier(order_id, item_id):
    """
    تعيين أو تغيير المورد المسؤول عن عنصر/منتج معين في الطلب
    """
    try:
        data = request.get_json() or {}
        supplier_id = data.get('supplier_id') or None

        # 1. تحديث المورد المسؤول عن المنتج في جدول عناصر الطلب
        db.session.execute(
            db.text("""
                UPDATE order_items 
                SET supplier_id = :supplier_id 
                WHERE id = :item_id AND order_id = :order_id
            """),
            {'supplier_id': supplier_id, 'item_id': item_id, 'order_id': order_id}
        )
        db.session.commit()

        # 2. توثيق الحركة في سجل المراجعة
        _record_audit_log(
            action='ASSIGN_SUPPLIER',
            details=f'تم تعيين المورد #{supplier_id} للمنتج #{item_id} في الطلب #{order_id}'
        )

        return jsonify({
            'success': True,
            'message': 'تم تعيين المورد بنجاح',
            'supplier_id': supplier_id
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error assigning supplier for item {item_id}: {str(e)}")
        return jsonify({'success': False, 'message': f'حدث خطأ أثناء تعيين المورد: {str(e)}'}), 500


def _record_audit_log(action, details):
    """
    دالة مساعدة لتوثيق السجلات آلياً وحمايتها بحيث لا يتوقف التطبيق حتى لو كان جدول audit_logs غير موجود
    """
    try:
        db.session.execute(
            db.text("""
                INSERT INTO audit_logs (action, details, created_at) 
                VALUES (:action, :details, NOW())
            """),
            {'action': action, 'details': details}
        )
        db.session.commit()
    except Exception as audit_err:
        db.session.rollback()
        current_app.logger.warning(f"Failed to record audit log [{action}]: {str(audit_err)}")
