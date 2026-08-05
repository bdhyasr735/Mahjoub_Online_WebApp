# 📂 apps/admin_orders/routes/actions.py
from flask import Blueprint, request, jsonify, current_app, render_template
from apps.extensions import db

# تم ضبط اسم الـ Blueprint إلى 'admin_order_actions' ليتطابق مع url_for في القوالب
actions_bp = Blueprint('admin_order_actions', __name__)


@actions_bp.route('/admin/orders/<order_id>/print', methods=['GET'])
def print_order_invoice(order_id):
    """
    عرض/طباعة فاتورة الطلب
    """
    try:
        # طباعة بسيطة للطلب، أو استدعاء قالب الفاتورة المخصص
        return f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>فاتورة رقم #{order_id}</title>
            <style>
                body {{ font-family: sans-serif; padding: 20px; }}
                @media print {{ .no-print {{ display: none; }} }}
            </style>
        </head>
        <body>
            <button class="no-print" onclick="window.print()">طباعة الفاتورة</button>
            <h2>تفاصيل فاتورة الطلب #{order_id}</h2>
            <hr>
            <p>تم استخراج الفاتورة بنجاح.</p>
        </body>
        </html>
        """
    except Exception as e:
        current_app.logger.error(f"Error printing order {order_id}: {str(e)}")
        return f"حدث خطأ أثناء إعداد الفاتورة: {str(e)}", 500


@actions_bp.route('/admin/orders/<order_id>/update-status', methods=['POST'])
def update_order_status(order_id):
    """
    تحديث حالة الطلب
    """
    try:
        data = request.get_json() or {}
        new_status = data.get('status')

        if not new_status:
            return jsonify({'success': False, 'message': 'حالة الطلب غير محددة'}), 400

        db.session.execute(
            db.text("UPDATE orders SET status = :status WHERE id = :order_id"),
            {'status': new_status, 'order_id': order_id}
        )
        db.session.commit()

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
    تعيين المورد للمنتج داخل الطلب
    """
    try:
        data = request.get_json() or {}
        supplier_id = data.get('supplier_id') or None

        db.session.execute(
            db.text("""
                UPDATE order_items 
                SET supplier_id = :supplier_id 
                WHERE id = :item_id AND order_id = :order_id
            """),
            {'supplier_id': supplier_id, 'item_id': item_id, 'order_id': order_id}
        )
        db.session.commit()

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
    حفظ السجلات بدون إيقاف السيرفر في حال عدم وجود الجدول
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
