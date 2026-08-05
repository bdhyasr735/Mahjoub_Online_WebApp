# coding: utf-8
# 📂 apps/admin_orders/routes/actions.py

from flask import Blueprint, request, jsonify, current_app, session
from flask_login import login_required
from apps.extensions import db

# ✅ تعريف actions_bp بالاسم المطابق تماماً لعملية الاستيراد في النظام
actions_bp = Blueprint(
    'admin_order_actions', 
    __name__,
    url_prefix='/admin/orders'
)

@actions_bp.route('/<order_id>/print', methods=['GET'])
@login_required
def print_order_invoice(order_id):
    """
    عرض/طباعة فاتورة الطلب
    """
    try:
        if session.get('user_type') != 'admin':
            return "غير مصرح لك بالوصول", 403

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


@actions_bp.route('/<order_id>/update-status', methods=['POST'])
@login_required
def update_order_status(order_id):
    """
    تحديث حالة الطلب
    """
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'message': 'غير مصرح لك بذلك'}), 403

        data = request.get_json() or {}
        new_status = data.get('status')

        if not new_status:
            return jsonify({'success': False, 'message': 'حالة الطلب غير محددة'}), 400

        db.session.execute(
            db.text("UPDATE orders SET status_code = :status WHERE id = :order_id"),
            {'status': new_status, 'order_id': order_id}
        )
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'تم تحديث حالة الطلب بنجاح',
            'status': new_status
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating order {order_id} status: {str(e)}")
        return jsonify({'success': False, 'message': f'حدث خطأ أثناء التحديث: {str(e)}'}), 500


@actions_bp.route('/<order_id>/item/<item_id>/assign-supplier', methods=['POST'])
@login_required
def assign_item_supplier(order_id, item_id):
    """
    تعيين المورد للمنتج داخل الطلب وتحديث خريطة الربط السيادية
    """
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'message': 'غير مصرح لك بذلك'}), 403

        data = request.get_json() or {}
        supplier_id = data.get('supplier_id') or None
        if supplier_id:
            supplier_id = int(supplier_id)

        # 1. تحديث المورد في عنصر الطلب الحالي
        db.session.execute(
            db.text("""
                UPDATE order_items 
                SET supplier_id = :supplier_id 
                WHERE id = :item_id AND order_id = :order_id
            """),
            {'supplier_id': supplier_id, 'item_id': item_id, 'order_id': order_id}
        )

        # 2. جلب product_qid لهذا العنصر لتحديث خريطة الربط السيادية إن وجد
        item_res = db.session.execute(
            db.text("SELECT product_qid FROM order_items WHERE id = :item_id"),
            {'item_id': item_id}
        ).fetchone()

        if item_res and item_res[0]:
            product_qid = item_res[0]
            # التحقق مما إذا كان الربط موجوداً مسبقاً في جدول product_supplier_mapping
            existing_map = db.session.execute(
                db.text("SELECT id FROM product_supplier_mapping WHERE product_qid = :qid"),
                {'qid': product_qid}
            ).fetchone()

            if existing_map:
                if supplier_id:
                    db.session.execute(
                        db.text("UPDATE product_supplier_mapping SET supplier_id = :supplier_id WHERE product_qid = :qid"),
                        {'supplier_id': supplier_id, 'qid': product_qid}
                    )
                else:
                    db.session.execute(
                        db.text("DELETE FROM product_supplier_mapping WHERE product_qid = :qid"),
                        {'qid': product_qid}
                    )
            elif supplier_id:
                db.session.execute(
                    db.text("INSERT INTO product_supplier_mapping (product_qid, supplier_id, status) VALUES (:qid, :supplier_id, 'active')"),
                    {'qid': product_qid, 'supplier_id': supplier_id}
                )

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'تم تعيين المورد وتحديث الخريطة بنجاح',
            'supplier_id': supplier_id
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error assigning supplier for item {item_id}: {str(e)}")
        return jsonify({'success': False, 'message': f'حدث خطأ أثناء تعيين المورد: {str(e)}'}), 500
